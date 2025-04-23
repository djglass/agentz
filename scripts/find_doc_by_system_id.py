from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("agentz_state/rag_index", embedding, allow_dangerous_deserialization=True)

target_id = "SYS-001641"
docs = vectorstore.similarity_search("placeholder", k=9999)

matches = [d for d in docs if d.metadata.get("system_id") == target_id]

print(f"🔎 Found {len(matches)} document(s) with system_id = {target_id}:\n")
for i, doc in enumerate(matches, 1):
    print(f"{i}. Source: {doc.metadata.get('source')} | Preview: {doc.page_content[:120]}...\n")

