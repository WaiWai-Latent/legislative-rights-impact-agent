import streamlit as st
import os
<<<<<<< HEAD
import time
=======
>>>>>>> origin/main
from io import BytesIO
import pdfplumber

# Import your backend functions
from src.reasoning import analyze
from src.diff_engine import diff_two_pdfs

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
<<<<<<< HEAD
# 2. ADVANCED CUSTOM CSS (Typography & Colors)
=======
# 2. ADVANCED CUSTOM CSS (Modern, High-Contrast)
>>>>>>> origin/main
# ==========================================
st.markdown("""
<style>
    /* Import Modern Fonts */
<<<<<<< HEAD
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* Apply Outfit to everything */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #111827, #030712);
        color: #f3f4f6;
=======
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* Apply font to everything */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Main Background - Deep Slate */
    .stApp {
        background: radial-gradient(circle at top right, #0f172a, #020617);
        color: #f8fafc;
>>>>>>> origin/main
    }
    
    /* Hide default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
<<<<<<< HEAD
        background: rgba(17, 24, 39, 0.95) !important;
=======
        background: rgba(15, 23, 42, 0.95) !important;
>>>>>>> origin/main
        border-right: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
    }

<<<<<<< HEAD
    /* Typography Colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
=======
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
>>>>>>> origin/main
        letter-spacing: -0.02em;
    }
    
    p, .stMarkdown p {
<<<<<<< HEAD
        color: #d1d5db !important; /* Light gray for readability */
=======
        color: #cbd5e1 !important; /* Light gray for readability */
>>>>>>> origin/main
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Hero Header */
    .hero-title {
<<<<<<< HEAD
        font-size: 3.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #60a5fa, #c084fc);
=======
        font-size: 3.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #38bdf8, #a78bfa);
>>>>>>> origin/main
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        line-height: 1.1;
<<<<<<< HEAD
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #9ca3af;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.01em;
=======
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 400;
>>>>>>> origin/main
    }

    /* Glassmorphism Cards */
    .glass-card {
<<<<<<< HEAD
        background: rgba(31, 41, 55, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
=======
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
>>>>>>> origin/main
        backdrop-filter: blur(12px);
        margin-bottom: 1rem;
    }
    
    /* Neon Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: #ffffff;
        border: none;
<<<<<<< HEAD
        font-family: 'Outfit', sans-serif;
=======
        font-family: 'Plus Jakarta Sans', sans-serif;
>>>>>>> origin/main
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.6);
        color: #ffffff;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
<<<<<<< HEAD
        background-color: rgba(17, 24, 39, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        font-family: 'Outfit', sans-serif !important;
=======
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
>>>>>>> origin/main
    }
    .stTextInput>div>div>input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3) !important;
    }

<<<<<<< HEAD
    /* Audit Trail Mono Font */
    .citation-text {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        color: #a78bfa !important; /* Purple accent */
        background: rgba(139, 92, 246, 0.1);
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 5px;
=======
    /* Audit Trail Citations */
    .citation-text {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        color: #a78bfa !important;
        background: rgba(139, 92, 246, 0.15);
        padding: 4px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-top: 8px;
>>>>>>> origin/main
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
<<<<<<< HEAD
        background-color: rgba(31, 41, 55, 0.5);
        border-radius: 8px;
        padding: 10px 20px;
        color: #9ca3af;
        border: 1px solid rgba(255,255,255,0.05);
        font-family: 'Outfit', sans-serif;
=======
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        padding: 10px 20px;
        color: #94a3b8;
        border: 1px solid rgba(255,255,255,0.05);
>>>>>>> origin/main
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: #ffffff !important;
        border: none;
    }
</style>
<<<<<<< HEAD
""", unsafe_allow_html=True)
=======
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>⚖️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>LCIS Platform</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # API KEY INPUT
    st.markdown("### 🔑 API Configuration")
    api_key_input = st.text_input("xAI (Grok) API Key", type="password", help="Paste your key here.")
    
    active_key = os.getenv("XAI_API_KEY") if os.getenv("XAI_API_KEY") else api_key_input
    
    if active_key:
        st.success("API Key Active")
    else:
        st.warning("⚠️ Enter API Key above.")
        
    st.markdown("---")
    
    st.markdown("### ⚙️ Engine Settings")
    top_k = st.slider("Retrieval Depth", 3, 10, 5, help="Number of document chunks used to ground the AI.")
    
    st.markdown("---")
    st.markdown("### 🛡️ Architecture")
    st.markdown("""
    <div style='color: #94a3b8; font-size: 0.9rem;'>
    ✅ Hybrid Search<br>
    ✅ Zero Hallucination<br>
    ✅ Per-Claim Citations<br>
    ✅ PDF Diffing
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MAIN UI HEADER
# ==========================================
st.markdown('<p class="hero-title">Legislative Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Transform dense government notifications into actionable, cited insights.</p>', unsafe_allow_html=True)

# ==========================================
# 5. TABS (RAG & DIFF)
# ==========================================
tab_rag, tab_diff = st.tabs(["🔍 Impact Analysis", "🔄 Version Diff Engine"])

# --- TAB 1: RAG ---
with tab_rag:
    st.markdown("### 💡 Quick Prompts")
    
    # Initialize session state for the query
    if "query_text" not in st.session_state:
        st.session_state.query_text = ""

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Mission Shakti Rules"): 
            st.session_state.query_text = "What are the main guidelines under Mission Shakti?"
    with col2:
        if st.button("MSME Scheme 2025"): 
            st.session_state.query_text = "Who is eligible for the MSME scheme?"
    with col3:
        if st.button("🛑 Anti-Hallucination Test"): 
            st.session_state.query_text = "What is the penalty for flying a drone on Mars?"

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Text Input bound to Session State
    query = st.text_input(
        "Ask a question about the ingested documents:", 
        value=st.session_state.query_text,
        placeholder="e.g., What are the compliance requirements for social audits?"
    )
    
    # Update session state if user types manually
    st.session_state.query_text = query

    generate_btn = st.button("Generate Grounded Analysis", type="primary")

    # Processing Logic
    if generate_btn or (query and st.session_state.query_text):
        if not query.strip():
            st.warning("Please enter a question.")
        elif not active_key:
            st.error("Please enter your API Key in the sidebar.")
        else:
            with st.spinner("Searching documents and reasoning..."):
                try:
                    out = analyze(query, top_k=top_k, api_key=active_key)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_ans, col_src = st.columns([2.5, 1])
                    
                    # Left: Answer (Using Streamlit's native markdown for proper formatting)
                    with col_ans:
                        with st.container(border=True):
                            st.markdown("### 📋 Analysis Report")
                            st.markdown(out["answer"])
                        
                    # Right: Audit Trail
                    with col_src:
                        st.markdown("### 📎 Audit Trail")
                        st.caption("The AI grounded its answer in these chunks:")
                        for s in out["sources"]:
                            st.markdown(f"""
                            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.8rem;">
                                <strong style='color: #f8fafc; font-size: 1rem;'>📄 {s['source']}</strong><br>
                                <div class="citation-text">Chunk {s['chunk']} | Score: {s['score']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")

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
>>>>>>> origin/main
