import os
import pdfplumber
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

# ====================== CONFIG ======================
DATA_DIR = "data/raw"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "govt_notifications"

# ====================== SETUP ======================
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)

# ====================== HELPERS ======================
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract clean text from PDF"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text.strip()


def chunk_text(text: str) -> list[str]:
    """Better chunking for legal/government documents"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=180,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len
    )
    return splitter.split_text(text)


def ingest_pdf(pdf_path: str, source_name: str = None):
    """Ingest a single PDF into the vector store"""
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    source_name = source_name or os.path.basename(pdf_path)
    print(f"\n📄 Processing: {source_name}")

    # 1. Extract text
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        print("⚠️  No text extracted.")
        return

    # 2. Chunking
    chunks = chunk_text(full_text)
    print(f"   → Created {len(chunks)} chunks")

    # 3. Prepare data
    ids = [f"{source_name}_{i}" for i in range(len(chunks))]
    metadatas = [{
        "source": source_name,
        "chunk_id": i,
        "ingested_at": datetime.now().isoformat()
    } for i in range(len(chunks))]

    # 4. Add to Chroma
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    print(f"   ✅ Successfully added {len(chunks)} chunks")


def ingest_all_pdfs():
    """Ingest all PDFs from data/raw folder"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Created folder: {DATA_DIR}")
        print("   Please put your PDF files inside data/raw/ and run again.")
        return

    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("❌ No PDF files found in data/raw/")
        return

    print(f"Found {len(pdf_files)} PDF files. Starting ingestion...\n")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        ingest_pdf(pdf_path)

    print(f"\n🎉 Done! Total chunks in database: {collection.count()}")


# ====================== RUN ======================
if __name__ == "__main__":
    ingest_all_pdfs()