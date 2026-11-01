# src/reasoning.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.system_prompt import SYSTEM_PROMPT
from src.retrieval import hybrid_retrieve

load_dotenv()

def build_context(chunks):
    lines = []
    for i, c in enumerate(chunks):
        src = c["metadata"]["source"]
        cid = c["metadata"]["chunk_id"]
        lines.append(f"[Chunk {i+1} | source: {src}, chunk {cid}]\n{c['text']}\n")
    return "\n".join(lines)

def analyze(query: str, top_k: int = 6, api_key: str = None):
    chunks = hybrid_retrieve(query, top_k=top_k)
    if not chunks:
        return {"answer": "No documents ingested yet.", "sources": [], "confidence": "None"}

    key_to_use = api_key if api_key else os.getenv("XAI_API_KEY")
    if not key_to_use:
        raise ValueError("xAI API key is missing. Please add it in the sidebar.")

    # We add a 120-second timeout here so Grok has enough time to reason
    client = OpenAI(
        api_key=key_to_use,
        base_url="https://api.x.ai/v1",
        timeout=120.0 
    )

    context = build_context(chunks)
    user_msg = f"CONTEXT:\n{context}\n\nQUESTION: {query}\n\nProvide grounded analysis."

    # The request call
    resp = client.chat.completions.create(
        model="grok-4.5", 
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
        timeout=120.0 # Also set it here for redundancy
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