# scripts/inspect_vectorstore.py

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

index_path = "agentz_state/rag_index"
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(index_path, embeddings=embedding, allow_dangerous_deserialization=True)

print("🔎 Inspecting top 5 documents with metadata:")
results = vectorstore.similarity_search("test", k=5)
for i, doc in enumerate(results, 1):
    print(f"\n--- Document #{i} ---")
    print("Content preview:", doc.page_content[:120])
    print("Metadata:", doc.metadata)
