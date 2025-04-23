# agentz/rag/retriever.py

class VectorstoreRetriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve_by_metadata_tag(self, tag: str, values: list, k: int = 5) -> list:
        """
        Simulates metadata filtering by post-processing FAISS results.
        LangChain's FAISS wrapper does not support filter= reliably.
        """
        values_set = set(values)
        all_matches = []

        try:
            docs = self.vectorstore.similarity_search("placeholder", k=10000)
            for doc in docs:
                if doc.metadata.get(tag) in values_set:
                    all_matches.append(doc)
        except Exception as e:
            print(f"⚠️ Failed to retrieve documents for tag '{tag}': {e}")

        return all_matches[:k * len(values)]

    def match_systems(self, cve_data: dict, cmdb_data: list) -> list:
        """
        Matches CVE fields against CMDB data using keyword-based fuzzy matching.
        Uses normalized fields and app keywords.
        """
        matched = []
        cve_keywords = set()

        for field in ["shortDescription", "products", "vendor"]:
            val = cve_data.get(field)
            if isinstance(val, list):
                for v in val:
                    cve_keywords.update(v.lower().split())
            elif isinstance(val, str):
                cve_keywords.update(val.lower().split())

        # Also include inferred keywords if present
        inferred = cve_data.get("inferred_keywords", [])
        cve_keywords.update(k.lower() for k in inferred)

        print(f"🔍 Matching CVE keywords: {sorted(cve_keywords)}")

        for i, system in enumerate(cmdb_data[:5]):
            fingerprint = (
                f"{system.get('hostname', '')} "
                f"{system.get('os', '')} "
                f"{system.get('Normalized OS', '')} "
                f"{system.get('Software', '')} "
                f"{system.get('Normalized Software', '')} "
                f"{' '.join(system.get('apps', []))}"
            ).lower()
            print(f"🧬 System #{i+1} fingerprint: {fingerprint}")

        for system in cmdb_data:
            fingerprint = (
                f"{system.get('hostname', '')} "
                f"{system.get('os', '')} "
                f"{system.get('Normalized OS', '')} "
                f"{system.get('Software', '')} "
                f"{system.get('Normalized Software', '')} "
                f"{' '.join(system.get('apps', []))}"
            ).lower()

            if any(kw in fingerprint for kw in cve_keywords):
                system["system_id"] = system.get("Asset Tag")
                matched.append(system)

        print(f"✅ Matched {len(matched)} system(s) to CVE {cve_data.get('cveID')}")
        return matched
