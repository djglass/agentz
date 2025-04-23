from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

INDEX_DIR = str(Path("agentz_state/rag_index"))

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    rdb = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    return rdb.as_retriever()
