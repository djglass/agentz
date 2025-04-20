from agentz.rag.index import get_faiss_index

def retrieve_context(query, k=5):
    index = get_faiss_index()
    docs = index.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in docs])
