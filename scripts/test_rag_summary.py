import os
from collections import Counter
from agentz.utils.tracker import lookup_cve, get_cmdb_data
from agentz.pipeline.pipeline_runner import RAGPipeline
from agentz.rag.retriever import VectorstoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def _generate_rollup(systems):
    risk_levels = Counter(s.get("risk_level", "Unknown") for s in systems)
    total = len(systems)
    lines = [f"Total matched systems: {total}"]
    for level in ["Critical", "High", "Medium", "Low", "Unknown"]:
        count = risk_levels.get(level, 0)
        if count:
            lines.append(f" • {level}: {count}")
    return "\n".join(lines)

def run_test_summary_for_cve(cve_id):
    print(f"\n🔍 TEST: CVE Summary for {cve_id}")

    cve = lookup_cve(cve_id)
    if not cve:
        print(f"❌ CVE {cve_id} not found.")
        return

    cmdb_data = get_cmdb_data()
    vectorstore = FAISS.load_local(
        "agentz_state/rag_index",
        embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        allow_dangerous_deserialization=True
    )
    retriever = VectorstoreRetriever(vectorstore)
    pipeline = RAGPipeline(cmdb_data=cmdb_data, retriever=retriever)

    prompt, matched_systems = pipeline.run(cve, return_systems=True)

    if not matched_systems:
        print("⚠️ No matched systems found.")
        return

    print("\n📊 Roll-Up Summary:")
    print(_generate_rollup(matched_systems))

    print("\n📋 Sample High-Risk Systems:")
    for s in matched_systems:
        if s.get("risk_level") in {"High", "Critical"}:
            print(f" • {s.get('hostname')} ({s.get('system_id')}) | Risk: {s['risk_level']} | Confidence: {s['confidence_score']}")

if __name__ == "__main__":
    run_test_summary_for_cve("CVE-2021-44228")
