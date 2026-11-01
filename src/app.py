import streamlit as st
import os
import time
from io import BytesIO
import pdfplumber

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
# 4. MAIN CONTENT AREA
# ==========================================
st.markdown('<p class="hero-title">Legislative Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Transform dense government notifications into actionable, cited insights.</p>', unsafe_allow_html=True)

# Create Tabs
tab_rag, tab_diff = st.tabs(["🔍 Impact Analysis", "🔄 Version Diff Engine"])

# --- TAB 1: RAG ---
with tab_rag:
    with st.container():
        # --- One-Click Example Queries ---
        st.markdown("### 🎯 Try an Example Question")
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
                    out = analyze(query, top_k=top_k)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_ans, col_src = st.columns([2.5, 1])
                    
                    # Left: Answer
                    with col_ans:
                        st.markdown(f"""
                        <div class="glass-card">
                            <h3 style='color: #38bdf8; margin-top: 0;'>📋 Analysis Report</h3>
                            <div style='color: #e2e8f0; line-height: 1.6;'>
                                {out["answer"]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    # Right: Audit Trail
                    with col_src:
                        st.markdown("### 📎 Audit Trail")
                        st.caption("The AI grounded its answer in these chunks:")
                        for s in out["sources"]:
                            st.markdown(f"""
                            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.5rem;">
                                <strong style='color: #a78bfa;'>📄 {s['source']}</strong><br>
                                <span style='font-size: 0.8rem; color: #94a3b8;'>Chunk {s['chunk']} | Score: {s['score']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                except Exception as e:
                    st.error(f"❌ API Error: {str(e)}\n\nPlease verify your GROQ_API_KEY in the .env file and that the model is available.")

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