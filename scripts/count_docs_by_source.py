from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from collections import Counter

index_path = "agentz_state/rag_index"
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(index_path, embeddings=embedding, allow_dangerous_deserialization=True)

# Count documents by source file
docs = vectorstore.similarity_search("test", k=9999)
source_counter = Counter(doc.metadata.get("source", "unknown") for doc in docs)

print("📊 Document count by source:")
for source, count in source_counter.items():
    print(f"{source}: {count}")

