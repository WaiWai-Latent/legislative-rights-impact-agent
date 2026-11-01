import streamlit as st
import os
import time
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
# 2. ADVANCED CUSTOM CSS (Typography & Colors)
# ==========================================
st.markdown("""
<style>
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* Apply Outfit to everything */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #111827, #030712);
        color: #f3f4f6;
    }
    
    /* Hide default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: rgba(17, 24, 39, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
    }

    /* Typography Colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    p, .stMarkdown p {
        color: #d1d5db !important; /* Light gray for readability */
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Hero Header */
    .hero-title {
        font-size: 3.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #9ca3af;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.01em;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(31, 41, 55, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
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
        font-family: 'Outfit', sans-serif;
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
        background-color: rgba(17, 24, 39, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        font-family: 'Outfit', sans-serif !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3) !important;
    }

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
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(31, 41, 55, 0.5);
        border-radius: 8px;
        padding: 10px 20px;
        color: #9ca3af;
        border: 1px solid rgba(255,255,255,0.05);
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: #ffffff !important;
        border: none;
    }
</style>
""", unsafe_allow_html=True)
