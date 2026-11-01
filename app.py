import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """You are an expert policy analyst helping ordinary citizens and small businesses understand government notifications.

Rules (strictly follow):
1. Only use information present in the provided document chunks.
2. If something is not clearly stated, say "Not clearly specified in the document".
3. Always cite the source by quoting short relevant phrases.
4. Use simple, clear language. Avoid legal jargon.
5. Structure your answer exactly in the format below.

Output Format:

### What Changed
- Clear bullet points of the actual changes

### Who is Affected
- List the groups of people or businesses affected
- Mention if anyone becomes newly eligible or ineligible

### Real-world Impact
- Practical effects in simple language
- Give 2-3 concrete examples if possible

### Source Citations
- Quote the most important original sentences and mention they come from the notification

### Confidence
- High / Medium / Low
- One line reason
"""

def generate_explanation(notification_text: str, retrieved_chunks: list[str] = None):
    context = "\n\n".join(retrieved_chunks) if retrieved_chunks else notification_text
    
    user_message = f"""
Here is the government notification content:

{context}

Please analyze it and generate the explanation following the exact format.
"""

    response = client.chat.completions.create(
        model="gpt-4o",  # or "claude-3-5-sonnet-20241022" etc.
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


# ======================
# UI
# ======================
st.title("⚖️ Multilingual Legislative Diff + Rights Impact Agent")
st.markdown("Upload a government notification and get a clear explanation of **what changed**, **who is affected**, and the **real-world impact**.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info("This tool explains complex government notifications in simple language with source citations.")
    st.markdown("---")
    st.markdown("**Current Scope (Hackathon)**")
    st.markdown("- Real official documents only\n- Strong source grounding\n- English (Hindi coming soon)")

# Main Area
uploaded_file = st.file_uploader("Upload Notification (PDF)", type=["pdf"])
manual_text = st.text_area("Or paste the notification text here:", height=200)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Generate Explanation", type="primary", use_container_width=True):
        if uploaded_file is None and not manual_text.strip():
            st.error("Please upload a PDF or paste text.")
        else:
            with st.spinner("Analyzing notification and generating grounded explanation..."):
                # Temporary: Use manual text or extracted text
                # Later replace this with Member A's retrieval
                text_content = manual_text.strip()
                
                if uploaded_file:
                    # Temporary placeholder - Member A will replace this
                    st.warning("PDF parsing will be connected from Member A's pipeline.")
                    text_content = "PDF support coming from data pipeline..." 

                if text_content:
                    explanation = generate_explanation(text_content)
                    st.session_state["explanation"] = explanation
                    st.session_state["original"] = text_content

with col2:
    st.markdown("### Tips for best results")
    st.markdown("""
    - Use official gazette / notification text
    - Longer relevant text = better explanation
    - Always check the citations
    """)

# Display Results
if "explanation" in st.session_state:
    st.markdown("---")
    st.subheader("📄 Generated Explanation")
    st.markdown(st.session_state["explanation"])

    with st.expander("View Original Text Used"):
        st.text(st.session_state["original"][:3000] + "..." if len(st.session_state["original"]) > 3000 else st.session_state["original"])