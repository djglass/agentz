# agentz/utils/prompts.py

def build_rag_prompt(cves: list[dict], include_risk_scoring: bool = True) -> str:
    if not cves:
        return "No CVEs provided."

    prompt_lines = [
        "You are a cybersecurity risk analyst.",
        "You have access to internal system architecture, configuration, and asset documentation provided in the retrieved context.",
        "You also have access to organizational security policies related to patching, configuration, access, incident response, and data classification.",
        "",
        "Use this information to assess the relevance and potential impact of the following CVEs on the organization’s environment.",
        "",
        "For each CVE:",
        "- Briefly explain what the vulnerability is.",
        "- Cross-reference it against the internal system documentation provided.",
        "- If a match is found (e.g., matching software, OS, hardware, service, or vendor), explain how this system may be at risk.",
        "- Evaluate the likelihood that the affected system is externally exposed to the internet.",
        "  * Use available IP addresses, firewall rules, and zone information to infer exposure.",
        "  * Systems using internal IPs (e.g., 10.x.x.x, 192.168.x.x) are generally not internet-facing.",
        "  * If firewall rules allow access from 'any' or external IP ranges, assume internet exposure.",
        "  * If the CVE has an 'internet_exposed' tag, assume it is reachable from the internet.",
        "  * If no exposure data is found, assume the system is internal by default.",
        "- Use organizational patch management and configuration policies to determine whether mitigation is likely to be enforced quickly.",
        "- Recommend a **primary mitigation action**. If a patch is available, this should typically be to apply the patch immediately.",
        "- You MUST reference relevant system types or OS matches even if the specific vulnerable component is not named.",
        "- Assume common services are present if OS or product type matches (e.g., assume Windows Server includes Print Spooler unless stated otherwise).",
        "- You must not speculate or fabricate matches. If no relevant system, software, vendor, or service is found in the retrieved context, clearly state: \"No matching internal systems found.\""
    ]

    if include_risk_scoring:
        prompt_lines.append("- Based on these factors, assign a **qualitative risk score**: High, Medium, or Low.")

    prompt_lines.extend([
        "- If no match is found, state that clearly.",
        "",
        "Then provide a high-level summary of key risk themes and possible business impacts.",
        "",
        "List of CVEs to evaluate:\n"
    ])

    for cve in cves:
        cve_id = cve.get("cveID", "UNKNOWN")
        vendor = cve.get("vendorProject", "UNKNOWN")
        product = cve.get("product", "UNKNOWN")
        description = (cve.get("shortDescription") or "").strip()
        risk = cve.get("qualitative_risk", "N/A")
        exposure = cve.get("exposure_vector", "unknown")
        criticality = cve.get("product_criticality", "low")
        known_exploited = cve.get("known_exploited", False)

        line = f"- {cve_id} — {vendor} {product}: {description}"
        if risk != "N/A":
            line += f" [Risk: {risk}, Exposure: {exposure.capitalize()}, Criticality: {criticality.capitalize()}]"
        if known_exploited:
            line += " [🔥 Known Exploited]"
        if cve.get("internet_exposed", False):
            line += " [⚠️ Internet-facing]"

        prompt_lines.append(line)

    prompt_lines.append(
        "\nRespond in plain English, structured and concise. Do not speculate beyond the provided documents, but infer risk based on reasonable assumptions about system configurations, security policy enforcement, and external exposure.\n"
        "Include a final line for each CVE: **Primary Mitigation Recommendation:**\n"
        "If no internal context applies, include: **Assessment Note:** No matching internal systems found. This vulnerability is not directly applicable."
    )

    return "\n".join(prompt_lines)


def build_prioritization_prompt(cve: dict, rollup_text: str) -> str:
    return f"""
You are a cyber risk advisor. The following CVE has been matched to enterprise systems:

CVE Metadata:
- ID: {cve['cveID']}
- Description: {cve.get('shortDescription', 'N/A')}
- Known Exploited: {cve.get('known_exploited', 'Unknown')}

Roll-Up Summary:
{rollup_text}

Based on the above, recommend how an enterprise should prioritize remediation:
- What environments or criticalities should be patched first?
- Should any factors override typical patch SLAs?
- Do NOT repeat the CVE description; focus only on prioritization logic.

Respond concisely, as if advising a CISO.
""".strip()


def build_deep_dive_prompt(cve: dict, top_systems_text: str) -> str:
    return f"""
You are a cyber risk analyst. A vulnerability (CVE) has been identified across the following high-risk systems:

CVE ID: {cve['cveID']}
Short Description: {cve.get('shortDescription', 'N/A')}

Top Impacted Systems:
{top_systems_text}

Provide a detailed analysis of why these systems are risky, and what remediation actions should be prioritized.
Focus on business-critical systems, exposure risks, and outdated patch levels.

Do NOT fabricate context. Only use the provided details.
""".strip()
