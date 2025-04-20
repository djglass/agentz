from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DOCS_DIR = Path("agentz_state/rag_index/docs")
INDEX_DIR = Path("agentz_state/rag_index")

def ingest_documents():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    texts = []
    metadatas = []

    for file in DOCS_DIR.glob("*"):
        if file.suffix.lower() in [".txt", ".csv", ".json"]:
            content = file.read_text(encoding="utf-8").strip()
            if content:
                texts.append(content)
                metadatas.append({"file": file.name})

    if not texts:
        print("⚠️ No documents found.")
        return

    db = FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)
    db.save_local(str(INDEX_DIR))
    print(f"✅ Ingested {len(texts)} documents and saved to {INDEX_DIR}")

if __name__ == "__main__":
    ingest_documents()
