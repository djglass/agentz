import argparse
import os
from agentz.utils.tracker import (
    get_new_cves,
    lookup_cve,
    log_summary,
    get_cmdb_data
)
from agentz.utils.rollup import generate_risk_rollup, summarize_high_risk_systems
from agentz.rag.prompts import (
    build_rag_prompt,
    build_prioritization_prompt,
    build_deep_dive_prompt
)
from agentz.pipeline.pipeline_runner import RAGPipeline
from agentz.rag.retriever import VectorstoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from agentz.llm.llm_router import call_llm_with_context

# Prevent tokenizer fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def summarize_cve(cve_id, show_details=False):
    print(f"🔍 Summarizing {cve_id}...")

    # Retrieve CVE metadata
    cve = lookup_cve(cve_id)
    if not cve:
        print(f"❌ Skipping CVE {cve_id} — no reliable metadata.")
        return

    # Load CMDB and vectorstore
    cmdb_data = get_cmdb_data()
    vectorstore = FAISS.load_local(
        "agentz_state/rag_index",
        embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        allow_dangerous_deserialization=True
    )
    retriever = VectorstoreRetriever(vectorstore)
    pipeline = RAGPipeline(cmdb_data=cmdb_data, retriever=retriever)

    # Run risk analysis pipeline
    prompt, matched_systems = pipeline.run(cve, return_systems=True)

    if matched_systems:
        rollup = generate_risk_rollup(matched_systems)
        print("\n📊 Roll-Up Summary:")
        print(rollup)

        if show_details:
            print(f"\n📋 High-Risk Systems for {cve_id}:\n")
            print(summarize_high_risk_systems(matched_systems))

    # Step 1: Risk Assessment
    response_1 = call_llm_with_context(prompt, vectorstore, cve_id)
    print(f"\n📝 Summary for {cve_id}:\n{response_1.strip()}")

    # Step 2: Prioritization Guidance
    prioritization_prompt = build_prioritization_prompt(cve, rollup)
    response_2 = call_llm_with_context(prioritization_prompt, vectorstore, cve_id)
    print(f"\n🚨 Prioritization Guidance:\n{response_2.strip()}")

    # Step 3: Optional Deep Dive if high-risk systems exist
    top_systems = summarize_high_risk_systems(matched_systems)
    if "No high-risk systems identified." not in top_systems:
        deep_dive_prompt = build_deep_dive_prompt(cve, top_systems)
        response_3 = call_llm_with_context(deep_dive_prompt, vectorstore, cve_id)
        print(f"\n🔍 Deep Dive on High-Risk Systems:\n{response_3.strip()}")

    # Log result (excluding deep dive for now)
    full_summary = f"{response_1}\n\n{response_2}"
    log_summary(cve_id, full_summary)

def main():
    parser = argparse.ArgumentParser(description="Summarize CVEs with enterprise risk context.")
    parser.add_argument("--cve", help="Summarize a specific CVE")
    parser.add_argument("--since", action="store_true", help="Summarize new CVEs since last run")
    parser.add_argument("--details", action="store_true", help="Include high-risk system details")
    args = parser.parse_args()

    if args.cve:
        summarize_cve(args.cve, show_details=args.details)
    elif args.since:
        new_cves = get_new_cves()
        if not new_cves:
            print("✅ No new CVEs to summarize.")
        else:
            for cve in new_cves:
                summarize_cve(cve["cveID"], show_details=args.details)
    else:
        print("❗ Please specify either --cve <CVE-ID> or --since")

if __name__ == "__main__":
    main()
