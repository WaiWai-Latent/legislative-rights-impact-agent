# src/retrieval.py
import os
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "govt_notifications"

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME, embedding_function=_embed_fn
)

# ---- Build BM25 index lazily on first query ----
_bm25 = None
_bm25_docs = None
_bm25_ids = None

def _build_bm25():
    global _bm25, _bm25_docs, _bm25_ids
    all_data = _collection.get(include=["documents", "metadatas"])
    _bm25_docs = all_data["documents"]
    _bm25_ids = all_data["ids"]
    tokenized = [doc.lower().split() for doc in _bm25_docs]
    _bm25 = BM25Okapi(tokenized)

def hybrid_retrieve(query: str, top_k: int = 6, alpha: float = 0.6):
    """
    alpha=0.6 means 60% weight on dense (semantic), 40% on BM25 (keyword).
    Returns list of {id, text, metadata, score}
    """
    global _bm25
    if _bm25 is None:
        _build_bm25()

    # --- Dense results ---
    dense = _collection.query(query_texts=[query], n_results=top_k * 2)
    dense_ids = dense["ids"][0]
    dense_docs = dense["documents"][0]
    dense_meta = dense["metadatas"][0]
    dense_dist = dense["distances"][0]
    # convert distance -> similarity
    dense_scores = {i: 1 - d for i, d in zip(dense_ids, dense_dist)}

    # --- BM25 results ---
    bm25_scores = _bm25.get_scores(query.lower().split())
    bm25_map = dict(zip(_bm25_ids, bm25_scores))

    # normalize BM25 to [0,1]
    if bm25_scores.max() > 0:
        max_b = max(bm25_scores)
        bm25_map = {k: v / max_b for k, v in bm25_map.items()}

    # --- Combine ---
    all_ids = set(dense_ids) | set(bm25_map.keys())
    combined = []
    for cid in all_ids:
        d = dense_scores.get(cid, 0.0)
        b = bm25_map.get(cid, 0.0)
        score = alpha * d + (1 - alpha) * b
        # find text + metadata
        if cid in dense_ids:
            idx = dense_ids.index(cid)
            text = dense_docs[idx]
            meta = dense_meta[idx]
        else:
            idx = _bm25_ids.index(cid)
            text = _bm25_docs[idx]
            meta = _collection.get(ids=[cid])["metadatas"][0]
        combined.append({"id": cid, "text": text, "metadata": meta, "score": score})

    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined[:top_k]


if __name__ == "__main__":
    for r in hybrid_retrieve("railway amendment penalty", top_k=3):
        print(f"[{r['score']:.3f}] {r['metadata']['source']} — {r['text'][:120]}...")
