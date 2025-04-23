# agentz/pipeline/context_engine.py

class ContextEngine:
    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve_documents(self, system_ids: list) -> list:
        """
        Retrieves relevant documents tied to the given list of system IDs
        using the retriever's metadata filtering logic.
        """
        if not system_ids:
            return []

        print(f"🧾 Requesting RAG for system_id: {system_ids}")
        print(f"🔍 Retrieving context for {len(system_ids)} matched systems...")
        docs = self.retriever.retrieve_by_metadata_tag("system_id", system_ids, k=5)
        return docs
