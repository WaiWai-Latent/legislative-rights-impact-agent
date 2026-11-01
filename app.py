# app.py
import streamlit as st
from src.reasoning import analyze

st.set_page_config(page_title="Legislative Change Intelligence", layout="wide")
st.title("⚖️ Legislative Change Intelligence System")
st.caption("Grounded impact analysis over ingested government notifications")

query = st.text_input("Ask about a notification / amendment / scheme:",
                      placeholder="e.g. What changed in the 2024 railway amendment?")
top_k = st.slider("Chunks to retrieve", 3, 10, 6)

if st.button("Analyze") and query:
    with st.spinner("Retrieving + reasoning..."):
        out = analyze(query, top_k=top_k)
    st.markdown("### 📋 Impact Analysis")
    st.markdown(out["answer"])
    st.markdown("### 📎 Retrieved Sources")
    for s in out["sources"]:
        st.write(f"- **{s['source']}** (chunk {s['chunk']}) — score {s['score']}")