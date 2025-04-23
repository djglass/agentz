from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

index_path = "agentz_state/rag_index"
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(index_path, embeddings=embedding, allow_dangerous_deserialization=True)

# Fetch top documents with a dummy query
docs = vectorstore.similarity_search("test", k=10)

print("🔍 First 10 documents and their system_id/source metadata:\n")
for i, doc in enumerate(docs, start=1):
    system_id = doc.metadata.get("system_id", "None")
    source = doc.metadata.get("source", "unknown")
    print(f"{i}. system_id: {system_id} | source: {source}")

