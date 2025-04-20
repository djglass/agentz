from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain_community.llms import Ollama
import os

INDEX_DIR = os.path.join(os.path.dirname(__file__), "../../../agentz_state/rag_index")

def get_contextual_risk_summary(cve_prompt: str) -> str:
    # Load index
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(INDEX_DIR, embedding_model, allow_dangerous_deserialization=True)

    # Search context
    related_docs = db.similarity_search(cve_prompt, k=4)
    if not related_docs:
        return "No relevant internal documents found for context."

    # Initialize model
    llm = Ollama(model="deepseek-coder:6.7b", temperature=0.3)

    # Load chain
    chain = load_qa_with_sources_chain(llm, chain_type="stuff")

    # Execute chain
    answer = chain.run({"input_documents": related_docs, "question": cve_prompt})
    return answer

def build_rag_prompt(cves: list[dict]) -> str:
    lines = ["Using internal security policies and asset knowledge, summarize the implications of the following CVEs:\n"]
    for cve in cves:
        cve_id = cve.get("cveID", "UNKNOWN")
        description = cve.get("shortDescription", "No description.")
        lines.append(f"- {cve_id}: {description}")
    lines.append("\nSummarize key themes and risks in plain English.")
    return "\n".join(lines)


