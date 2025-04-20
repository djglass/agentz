import argparse
from pathlib import Path

from agentz.llm.base import summarize_text
from agentz.utils.tracker import get_recent_cves, lookup_cve
from agentz.rag.prompts import build_rag_prompt

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

RAG_INDEX_DIR = Path("agentz_state/rag_index")

# Load FAISS-based RAG retriever
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
try:
    db = FAISS.load_local(str(RAG_INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"❌ Failed to load FAISS index from {RAG_INDEX_DIR}: {e}")
    exit(1)

retriever = db.as_retriever()
rqa = RetrievalQA.from_chain_type(
    llm=summarize_text.llm,
    retriever=retriever,
    chain_type="stuff"
)

def rag_summarize_cves(cves: list[dict]) -> str:
    prompt = build_rag_prompt(cves)
    result = rqa.invoke({"query": prompt})
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG-based CVE summarizer")
    parser.add_argument("--cve", help="Specify a CVE ID to summarize (e.g., CVE-2024-1234)")
    args = parser.parse_args()

    if args.cve:
        cve = lookup_cve(args.cve)
        if not cve:
            print(f"⚠️ CVE '{args.cve}' not found in KEV feed.")
            exit(1)
        cves = [cve]  # wrap in list for compatibility
    else:
        cves = get_recent_cves(limit=3)
        if not cves:
            print("⚠️ No recent CVEs found in seen list.")
            exit(1)

    print("\n📥 CVEs:")
    for cve in cves:
        print(f" - {cve.get('cveID')}: {cve.get('shortDescription')}")

    print("\n🧠 Running RAG-based summarization...")
    summary = rag_summarize_cves(cves)
    print("\n📋 Summary:")
    print(summary)
