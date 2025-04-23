# scripts/test_pipeline.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agentz.pipeline.pipeline_runner import RAGPipeline
from agentz.rag.retriever import VectorstoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_vectorstore():
    index_path = "agentz_state/rag_index"
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(index_path, embeddings=embedding, allow_dangerous_deserialization=True)

sample_cmdb = [
    {"id": "SRV-00002", "hostname": "dc-server-2", "os": "Windows Server 2022", "apps": ["IIS", "Nessus"]},
    {"id": "SRV-00004", "hostname": "dc-server-4", "os": "Windows Server 2019", "apps": ["Tomcat", "Node.js"]},
]

sample_cve = {
    "id": "CVE-2023-1234",
    "description": "Microsoft IIS in Windows Server 2019 and 2022 is vulnerable to remote code execution.",
    "products": ["Windows Server 2022", "IIS"],
    "vendor": "Microsoft",
    "cpe": ["cpe:/o:microsoft:windows_server_2022"]
}

def main():
    print("🔍 Loading vectorstore...")
    vectorstore = load_vectorstore()
    retriever = VectorstoreRetriever(vectorstore)

    print("⚙️  Running 3-phase pipeline...")
    pipeline = RAGPipeline(cmdb_data=sample_cmdb, retriever=retriever)
    prompt = pipeline.run(sample_cve)

    print("\n📤 Final Prompt:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)

if __name__ == "__main__":
    main()
