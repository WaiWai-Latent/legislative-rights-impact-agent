# src/reasoning.py
import os
from dotenv import load_dotenv
from openai import OpenAI
<<<<<<< HEAD
from retrieval import hybrid_retrieve

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

model="openai/gpt-oss-20b"

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

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

def list_models():
    """List the model ids available to the configured Groq API key."""
# the model ids available to the configured Groq API key."""""""\"\""""\"\"\"
    try:
        return sorted(m.id for m in client.models.list().data)
    except Exception as exc:  # pragma: no cover - network/auth failures
        return [f"error: {exc}"]

=======
from src.system_prompt import SYSTEM_PROMPT
from src.retrieval import hybrid_retrieve

load_dotenv()
>>>>>>> origin/main

def build_context(chunks):
    lines = []
    for i, c in enumerate(chunks):
        src = c["metadata"]["source"]
        cid = c["metadata"]["chunk_id"]
        lines.append(f"[Chunk {i+1} | source: {src}, chunk {cid}]\n{c['text']}\n")
    return "\n".join(lines)

<<<<<<< HEAD
def analyze(query: str, top_k: int = 6, model: str = "openai/gpt-oss-20b"):
=======
def analyze(query: str, top_k: int = 6, api_key: str = None):
>>>>>>> origin/main
    chunks = hybrid_retrieve(query, top_k=top_k)
    if not chunks:
        return {"answer": "No documents ingested yet.", "sources": [], "confidence": "None"}

<<<<<<< HEAD
    context = build_context(chunks)
    user_msg = f"CONTEXT:\n{context}\n\nQUESTION: {query}\n\nProvide grounded analysis."

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1,
        )
    except Exception as exc:
        return {
            "answer": f"API Error: {exc}\n\nPlease check your GROQ_API_KEY in .env and that the model '{model}' is available (run list_models()).",
            "sources": [
                {
                    "source": c["metadata"]["source"],
                    "chunk": c["metadata"]["chunk_id"],
                    "score": round(c["score"], 3),
                }
                for c in chunks
            ],
            "confidence": "None",
        }
=======
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
>>>>>>> origin/main
    answer = resp.choices[0].message.content

    return {
        "answer": answer,
        "sources": [
<<<<<<< HEAD
            {
                "source": c["metadata"]["source"],
                "chunk": c["metadata"]["chunk_id"],
                "score": round(c["score"], 3),
                "text": c.get("text", ""),
            }
=======
            {"source": c["metadata"]["source"], "chunk": c["metadata"]["chunk_id"], "score": round(c["score"], 3)}
>>>>>>> origin/main
            for c in chunks
        ],
        "confidence": "see answer",
    }