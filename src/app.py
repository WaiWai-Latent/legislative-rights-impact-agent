import streamlit as st
import os
import time
from io import BytesIO
import pdfplumber

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reasoning import analyze
from diff_engine import diff_two_pdfs

# ==========================================
# 1. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="LCIS | Legislative Change Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. ADVANCED CUSTOM CSS (The "SaaS" Look)
# ==========================================
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        color: #f8fafc;
    }
    
    /* Hide default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
    }

    /* Headers */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #38bdf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(12px);
        margin-bottom: 1rem;
    }
    
    /* Neon Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.6);
        color: white;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3) !important;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 12px;
        padding: 1rem;
        border: 1px dashed #475569;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        padding: 10px 20px;
        color: #94a3b8;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
    }
    
    /* Expander (for Diff) */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.8);
        border-radius: 8px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>⚖️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>LCIS Platform</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### ⚙️ Engine Settings")
    top_k = st.slider("Retrieval Depth", 3, 10, 5, help="Number of document chunks used to ground the AI.")
    
    st.markdown("---")
    st.markdown("### 🛡️ System Architecture")
    st.markdown("""
    <div style='color: #94a3b8; font-size: 0.9rem;'>
    ✅ Hybrid Search (Dense + BM25)<br>
    ✅ Zero Hallucination Guard<br>
    ✅ Per-Claim Citations<br>
    ✅ Structural PDF Diffing
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("v1.0.0")

# ==========================================
# 0. STARTUP INGESTION (once per session)
# ==========================================
def _ensure_ingested():
    if st.session_state.get("ingestion_done"):
        return
    if st.session_state.get("ingestion_error"):
        st.error(f"Ingestion failed: {st.session_state['ingestion_error']}")
        return
    try:
        from retrieval import _collection
        if _collection.count() > 0:
            st.session_state["ingestion_done"] = True
            return
        with st.spinner("Ingesting committed policy PDFs into the vector store..."):
            from ingest import ingest_all_pdfs
            ingest_all_pdfs()
        if _collection.count() == 0:
            msg = "No documents were ingested. Check that PDFs exist under data/raw/."
            st.session_state["ingestion_error"] = msg
            st.error(msg)
        else:
            st.session_state["ingestion_done"] = True
    except Exception as e:
        st.session_state["ingestion_error"] = str(e)
        st.error(f"Ingestion failed: {e}")

_ensure_ingested()

# ==========================================
# 4. MAIN CONTENT AREA
# ==========================================
st.markdown('<p class="hero-title">Legislative Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Transform dense government notifications into actionable, cited insights.</p>', unsafe_allow_html=True)

# Create Tabs
tab_rag, tab_diff, tab_impact = st.tabs(["🔍 Impact Analysis", "🔄 Version Diff Engine", "📊 Policy Change Impact Graph"])

# --- TAB 1: RAG ---
with tab_rag:
    with st.container():
        # --- One-Click Example Queries ---
        st.markdown("### Try an Example Question")
        example_questions = [
            "What is Mission Shakti and who can benefit from it?",
            "What support does Mission Vatsalya provide for children?",
            "What are the key components of Comprehensive Primary Health Care?",
            "Who is eligible under Mission Saksham?",
        ]
        ex_cols = st.columns(2)
        example_q = None
        for idx, eq in enumerate(example_questions):
            with ex_cols[idx % 2]:
                if st.button(eq, key=f"example_q_{idx}"):
                    example_q = eq

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### 💡 Quick Prompts")
        
        # Quick Prompt Buttons
        col1, col2, col3 = st.columns(3)
        sample_q = None
        with col1:
            if st.button("Mission Shakti Rules"): sample_q = "What are the main guidelines under Mission Shakti?"
        with col2:
            if st.button("MSME Scheme 2025"): sample_q = "Who is eligible for the MSME scheme?"
        with col3:
            if st.button("🛑 Anti-Hallucination Test"): sample_q = "What is the penalty for flying a drone on Mars?"

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Search Bar
        query = st.text_input("Ask a question about the ingested documents:", value=(example_q or sample_q) if (example_q or sample_q) else "", placeholder="e.g., What are the compliance requirements for social audits?")
        
        generate_btn = st.button("Generate Grounded Analysis", type="primary")

    # Processing Logic
    if generate_btn or sample_q or example_q:
        if not query:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching documents and reasoning..."):
                try:
                    out = analyze(query, top_k=top_k) or {}
                    answer = out.get("answer", "") if isinstance(out, dict) else str(out)
                    sources = out.get("sources", []) if isinstance(out, dict) else []
                    confidence_raw = out.get("confidence", "") if isinstance(out, dict) else ""
                    confidence = str(confidence_raw).strip().lower()
                    if confidence in ("high", "medium", "low"):
                        badge_label = confidence.capitalize()
                    else:
                        badge_label = "Confidence unavailable"

                    # Confidence badge colors
                    color_map = {"high": "green", "medium": "orange", "low": "red"}
                    badge_color = color_map.get(confidence, "gray")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"### 📋 Analysis Report  \n<span style='color:{badge_color}; font-weight:600;'>Confidence: {badge_label}</span>", unsafe_allow_html=True)

                    # Structured sections: parse markdown headings
                    import re
                    sections = {}
                    current = "Answer / Overview"
                    sections[current] = []
                    for line in str(answer).splitlines():
                        m = re.match(r"^#{1,3}\s+(.+)$", line.strip())
                        if m:
                            heading = m.group(1).strip()
                            current = heading
                            sections.setdefault(current, [])
                        else:
                            sections.setdefault(current, []).append(line)
                    # Render each non-empty section as a card
                    for heading, lines in sections.items():
                        text = "\n".join(lines).strip()
                        if not text:
                            continue
                        with st.container():
                            st.markdown(f"**{heading}**")
                            st.markdown(text)

                    # Sources
                    if sources:
                        st.markdown("### Sources")
                        for s in sources:
                            name = s.get("source", "Unknown source") if isinstance(s, dict) else str(s)
                            chunk = s.get("chunk", "") if isinstance(s, dict) else ""
                            score = s.get("score", None) if isinstance(s, dict) else None
                            score_text = f" (score: {score})" if score is not None else ""
                            st.markdown(f"- **{name}**{score_text} — chunk {chunk}")

                    # Supporting Evidence panel
                    with st.expander("View Supporting Evidence", expanded=False):
                        evidence = (sources or [])[:4]
                        if not evidence:
                            st.info("No supporting evidence is available for this answer.")
                        else:
                            for i, ev in enumerate(evidence, 1):
                                if not isinstance(ev, dict):
                                    st.markdown(f"**Evidence {i}**\n\n{ev}")
                                    continue
                                name = ev.get("source") or "Unknown source"
                                score = ev.get("score", None)
                                text = ev.get("text", "")
                                st.markdown(f"**{i}. {name}**" + (f"  \nRelevance score: {score}" if score is not None else ""))
                                if text:
                                    st.markdown(f"> {text}")
                                else:
                                    st.caption("No text snippet available.")
                                if i < len(evidence):
                                    st.markdown("---")
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- TAB 2: DIFF ENGINE ---
with tab_diff:
    st.markdown("### 🆚 Compare Document Versions")
    st.markdown("<p style='color: #94a3b8;'>Upload the original PDF and the amended PDF to detect exact structural changes.</p>", unsafe_allow_html=True)
    
    col_old, col_new = st.columns(2)
    with col_old:
        old_file = st.file_uploader("Upload OLD Version (PDF)", type=["pdf"], key="old")
    with col_new:
        new_file = st.file_uploader("Upload NEW Version (PDF)", type=["pdf"], key="new")
        
    if st.button("Run Diff Analysis", type="primary") and old_file and new_file:
        with st.spinner("Extracting text and computing diff..."):
            os.makedirs("/tmp/lcis", exist_ok=True)
            p_old = f"/tmp/lcis/{old_file.name}"
            p_new = f"/tmp/lcis/{new_file.name}"
            
            with open(p_old, "wb") as f: f.write(old_file.read())
            with open(p_new, "wb") as f: f.write(new_file.read())
            
            try:
                changes = diff_two_pdfs(p_old, p_new)
                
                st.success(f"Diff Complete! Found {len(changes)} change blocks.")
                
                for c in changes:
                    with st.expander(f"Change Type: {c['type'].upper()}"):
                        if c['old']:
                            st.markdown("**Old Text (Removed):**")
                            for line in c['old']:
                                st.markdown(f"- ~~{line}~~")
                        if c['new']:
                            st.markdown("**New Text (Added):**")
                            for line in c['new']:
                                st.markdown(f"- **{line}**")
            except Exception as e:
                st.error(f"Diff failed: {e}")

# --- TAB 3: POLICY CHANGE IMPACT GRAPH ---
with tab_impact:
    st.markdown("### 📊 Policy Change Impact Graph")
    st.caption("Upload an earlier and a later version of the same policy document. No versions are fabricated; if you do not have two versions, this feature shows an empty state.")
    c1, c2 = st.columns(2)
    with c1:
        old_file = st.file_uploader("Earlier version (PDF)", type=["pdf"], key="impact_old")
    with c2:
        new_file = st.file_uploader("Later version (PDF)", type=["pdf"], key="impact_new")

    if st.button("Analyze Policy Changes", type="primary") and old_file and new_file:
        import os as _os
        _os.makedirs("/tmp/lcis", exist_ok=True)
        p_old = f"/tmp/lcis/{old_file.name}"
        p_new = f"/tmp/lcis/{new_file.name}"
        with open(p_old, "wb") as f:
            f.write(old_file.read())
        with open(p_new, "wb") as f:
            f.write(new_file.read())
        try:
            from diff_engine import diff_two_pdfs
            from impact_graph import build_impact_table, build_graph
            changes = diff_two_pdfs(p_old, p_new)
            rows = build_impact_table(changes)
            if not rows:
                st.info("No meaningful changes detected between the two documents.")
            else:
                st.markdown("#### Change Summary")
                for r in rows:
                    st.markdown(f"- **{r['category']}**")
                    st.markdown(f"  - Previous: {r['previous'] or '(none)'}")
                    st.markdown(f"  - New: {r['new'] or '(none)'}")
                st.markdown("#### Detailed Table")
                st.table(rows)

                # Node selection
                g = build_graph(rows)
                if g is not None:
                    nodes = list(g.nodes())
                    sel = st.selectbox("Inspect node", nodes)
                    if sel is not None:
                        st.markdown(f"**Node:** {sel}")
                        st.markdown(f"Type: {g.nodes[sel].get('type', 'unknown')}")
                        st.markdown("Edges:")
                        for u, v, d in g.edges(data=True):
                            if u == sel or v == sel:
                                st.markdown(f"- {u} → {v} ({d.get('relation','')})")

                # Evidence via RAG
                st.markdown("#### Evidence-Grounded Impact Analysis")
                query = "What are the impacts of the changes between these two policy versions?"
                try:
                    from reasoning import analyze
                    out = analyze(query, top_k=5)
                    st.markdown(out.get("answer", "") if isinstance(out, dict) else str(out))
                    if isinstance(out, dict) and not out.get("sources"):
                        st.warning("Insufficient evidence to determine impact.")
                except Exception as e:
                    st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Analysis failed: {e}")
    elif not (old_file and new_file):
        st.info("Upload both versions to analyze policy changes.")
