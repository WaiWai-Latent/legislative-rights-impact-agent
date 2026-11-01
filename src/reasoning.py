# src/reasoning.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.retrieval import hybrid_retrieve

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a Legislative Change Intelligence analyst.
You answer strictly from the provided context. Follow these rules:
1. NEVER invent facts. If the context does not contain the answer, say "Not found in provided documents."
2. Every factual claim MUST end with a citation like [source: filename, chunk N].
3. Structure your answer as:
   - **Summary** (2-3 sentences)
   - **What Changed / Key Provisions** (bulleted)
   - **Who Is Affected**
   - **Rights / Compliance Impact**
   - **Confidence**: High / Medium / Low (based on how well context supports the answer)
"""

def build_context(chunks):
    lines = []
    for i, c in enumerate(chunks):
        src = c["metadata"]["source"]
        cid = c["metadata"]["chunk_id"]
        lines.append(f"[Chunk {i+1} | source: {src}, chunk {cid}]\n{c['text']}\n")
    return "\n".join(lines)

def analyze(query: str, top_k: int = 6, model: str = "gpt-4o-mini"):
    chunks = hybrid_retrieve(query, top_k=top_k)
    if not chunks:
        return {"answer": "No documents ingested yet.", "sources": [], "confidence": "None"}

    context = build_context(chunks)
    user_msg = f"CONTEXT:\n{context}\n\nQUESTION: {query}\n\nProvide grounded analysis."

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )
    answer = resp.choices[0].message.content

    return {
        "answer": answer,
        "sources": [
            {"source": c["metadata"]["source"], "chunk": c["metadata"]["chunk_id"], "score": round(c["score"], 3)}
            for c in chunks
        ],
        "confidence": "see answer",
    }


if __name__ == "__main__":
    out = analyze("What changed in the latest railway notification and who is affected?")
    print(out["answer"])
    print("\n--- Sources ---")
    for s in out["sources"]:
        print(s)