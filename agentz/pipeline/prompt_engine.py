# agentz/pipeline/prompt_engine.py

class PromptEngine:
    def build_prompt(self, cve_data: dict, matched_systems: list, context_docs: list) -> str:
        summary_stats = self._build_rollup_summary(matched_systems)
        impacted_section = self._build_impacted_section(matched_systems)
        context_section = self._build_context_section(context_docs)

        instructions = (
            "**Instructions for Analysis**\n"
            "You are a cybersecurity threat analyst. Analyze the risk this CVE poses to the systems listed below.\n"
            "- Prioritize systems that are internet-exposed, have high criticality, or belong to sensitive departments.\n"
            "- For unknown systems that match the CVE, assume they may be vulnerable unless contradicted by strong evidence.\n"
            "- Use the confidence score to assess likelihood of impact.\n"
            "- Recommend prioritized mitigations.\n"
            "- End your analysis with a brief roll-up summary.\n"
        )

        return f"""[CVE]
{cve_data.get('cveID')}: {cve_data.get('shortDescription', 'No summary available')}

{summary_stats}

[Impacted Systems]
{impacted_section}

[Supporting Context]
{context_section}

{instructions}
**[End of Log]**
"""

    def _build_impacted_section(self, systems: list) -> str:
        lines = []
        for s in systems:
            line = f"- {s.get('hostname', 'Unknown')} ({s.get('os', 'Unknown OS')}) | Confidence Score: {s.get('confidence_score', 0)}/100 | Exposure: {s.get('exposure', 'unknown')} | Criticality: {s.get('criticality', 'unknown')}"
            lines.append(line)
        return "\n".join(lines) if lines else "None"

    def _build_context_section(self, docs: list) -> str:
        chunks = []
        for doc in docs:
            system_id = doc.metadata.get("system_id", "unknown")
            chunks.append(f"[{system_id}] {doc.page_content.strip()[:500]}")
        return "\n\n".join(chunks) if chunks else "None"

    def _build_rollup_summary(self, systems: list) -> str:
        from collections import Counter

        exposure_counts = Counter(s.get("exposure", "unknown") for s in systems)
        crit_counts = Counter(s.get("criticality", "unknown") for s in systems)
        total = len(systems)

        summary = [
            "**Roll-Up Risk Summary**",
            f"- Total matched systems: {total}",
            f"- Internet-exposed: {exposure_counts.get('internet', 0)}",
            f"- Datacenter: {exposure_counts.get('datacenter', 0)}",
            f"- Cloud: {exposure_counts.get('cloud', 0)}",
            f"- End-user: {exposure_counts.get('endpoint', 0)}",
            "",
            f"- High criticality: {crit_counts.get('high', 0)}",
            f"- Medium criticality: {crit_counts.get('medium', 0)}",
            f"- Low criticality: {crit_counts.get('low', 0)}",
        ]
        return "\n".join(summary)
