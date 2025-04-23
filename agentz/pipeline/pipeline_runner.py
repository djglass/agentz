# agentz/pipeline/pipeline_runner.py

from agentz.utils.confidence import compute_confidence_score
from agentz.utils.risk import compute_risk_score
from agentz.utils.rollup import generate_risk_rollup
from agentz.llm.llm_router import call_llm_with_context


class RAGPipeline:
    def __init__(self, cmdb_data, retriever):
        self.cmdb_data = cmdb_data
        self.retriever = retriever

    def run(self, cve_data: dict, return_systems: bool = False):
        matched_systems = self.retriever.match_systems(cve_data, self.cmdb_data)
        for system in matched_systems:
            system["confidence_score"] = compute_confidence_score(system, cve_data)
            system["risk_level"], system["risk_score"] = compute_risk_score(system)

        # 🔁 Prompt Chain - Phase 1: Roll-Up Summary
        rollup_prompt = generate_risk_rollup(matched_systems)
        rollup_response = call_llm_with_context(rollup_prompt, self.retriever.vectorstore, query="rollup")

        # 🔁 Prompt Chain - Phase 2: Risk Assessment
        risk_prompt = self._build_risk_assessment_prompt(matched_systems, cve_data, rollup_response)
        risk_response = call_llm_with_context(risk_prompt, self.retriever.vectorstore, query="prioritization")

        # ⛓️ Chain: Combine into full output prompt
        full_prompt = f"{rollup_response}\n\n---\n\n{risk_response}"

        return (full_prompt, matched_systems) if return_systems else full_prompt

    def _build_risk_assessment_prompt(self, systems, cve_data, rollup_summary):
        system_lines = []
        for s in systems[:50]:  # limit to first 50 for summarization prompt
            line = f"{s.get('hostname', 'Unknown')} | Risk: {s.get('risk_level')} | Confidence: {s.get('confidence_score')} | Criticality: {s.get('Criticality')} | Environment: {s.get('Environment')}"
            system_lines.append(line)

        systems_block = "\n".join(system_lines)
        return (
            f"{rollup_summary}\n\n"
            f"---\n\n"
            f"The above roll-up summarizes risk for CVE {cve_data['cveID']}.\n\n"
            f"Below is a sample of 50 matched systems:\n\n"
            f"{systems_block}\n\n"
            f"Based on this data, identify the highest-risk systems and recommend prioritization steps.\n"
            f"Do not speculate about systems not listed. Focus on those with highest impact."
        )
