from agentz.llm.localstack_ollama import LocalstackOllamaLLM

def call_llm_with_context(prompt: str, vectorstore, query: str) -> str:
    retriever = vectorstore.as_retriever(search_type="similarity", k=6)
    docs = retriever.invoke(query)

    # 🔍 DEBUG: Show retrieved docs
    #print("\n📚 Retrieved RAG Context:")
    #    for i, doc in enumerate(docs):
    #    print(f"--- Doc {i+1} ---\n{doc.page_content[:500]}\n")

    context = "\n\n".join([doc.page_content for doc in docs])
    full_prompt = f"Context:\n{context}\n\n---\n\n{prompt}"

    llm = LocalstackOllamaLLM()
    return llm.invoke(full_prompt)

