# 🛡️ agentz — CVE Risk Summarization and Analysis Pipeline

`agentz` is a local-first cybersecurity assistant that evaluates Common Vulnerabilities and Exposures (CVEs) against internal enterprise environments using document-based RAG (Retrieval-Augmented Generation), CMDB context, and structured prompt chaining. It leverages locally hosted LLMs via Ollama and supports zero external dependencies or cloud calls.

---

## 🚀 Key Features

- **Risk-Aware RAG**: Summarizes CVEs using retrieved internal architecture, policy, and asset data.
- **Local LLM Inference**: Uses Ollama and DeepSeek for fast and secure local LLM inference.
- **CMDB Integration**: Filters affected systems based on real asset data (e.g., OS, software, zone).
- **Prompt Chaining**: Separates analysis into structured steps: roll-up, prioritization, and deep-dive.
- **Confidence Scoring**: Combines exposure, system metadata, and matching logic to compute risk.
- **CLI-first**: Runs from the terminal with flags like `--details` and `--since`.

---

## 🗂️ Project Structure

```
agentz_prj/
├── agentz/                  # Core logic
│   ├── pipeline/            # Orchestrates CVE summary + system filtering
│   ├── rag/                 # FAISS retriever, prompt builders
│   ├── llm/                 # CLI entry point, LLM router
│   ├── utils/               # CMDB loading, tracker, scoring, roll-up
├── agentz_state/            # Vector index and persistent metadata
├── scripts/                 # Test scripts, ingestion runners
├── data/                    # Input files: CMDB, firewall rules, policies
├── localstack_api/          # Local AWS Lambda + Gateway mock environment
```

---

## ⚙️ Usage

### 🔍 Analyze a Specific CVE
```bash
PYTHONPATH=. python agentz/llm/rag_summarize.py --cve CVE-2021-44228
```

### 📋 Include High-Risk System Details
```bash
PYTHONPATH=. python agentz/llm/rag_summarize.py --cve CVE-2021-44228 --details
```

### 🆕 Check for New CVEs Since Last Run
```bash
PYTHONPATH=. python agentz/llm/rag_summarize.py --since
```

---

## 🔗 LLM and RAG Setup

- **Vectorstore**: FAISS index stored at `agentz_state/rag_index/`
- **Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2`
- **LLM Serving**: Assumes Ollama/DeepSeek local API endpoint

---

## 📊 Prompt Chain Stages

Each CVE analysis includes:

1. **RAG-Enhanced Summary**: Evaluates systems, security policies, and business impacts.
2. **Prioritization Guidance**: Advises based on criticality, environment, and SLA overrides.
3. **(Optional) Deep Dive**: Explains why top systems are risky and how to remediate them.

---

## 🧪 Testing

Run the test suite (requires test data under `scripts/`):

```bash
PYTHONPATH=. python scripts/test_rag_summary.py
```

---

## 🧼 Hygiene & Maintenance

- Vectorstore state: `agentz_state/`
- Logs: `logs/` (optional, ignored by default)
- Ignore `.venv/`, `.env`, and `.git/` when zipping or syncing.

---

## 📌 Roadmap

- [ ] CLI pagination for large CVE outputs
- [ ] Web interface for CVE dashboard
- [ ] Threat intel feed ingestion (e.g., Abuse.ch, CIRCL)
- [ ] Real-time agent enrichment and attack surface detection

---

## 📜 License

Internal project — not for external distribution.
