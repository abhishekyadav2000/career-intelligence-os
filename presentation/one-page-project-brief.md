# One-Page Project Brief — Career Intelligence OS

## Problem
Enterprise technology hiring in DFW is fragmented across 50+ employers, hundreds of roles, and opaque sponsorship signals. Candidates lack a unified decision system to prioritize, score, prepare, and iterate.

## Solution
Career Intelligence OS — a sponsor-aware career intelligence system that ingests structured data, scores role fit across six categories, generates recommendations and outreach, maps interview prep, and closes the loop with conversation feedback.

## Universal Profile
**Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics**

## Key Metrics
| Metric | Value |
|--------|-------|
| Companies analyzed | 50 |
| Jobs scored | 117 |
| Contacts mapped | 75 |
| Scoring categories | 6 |
| Recommendation actions | 4 |
| Dashboard tabs | 9 |

## Architecture (One Line)
CSV data → validation → scoring engine → recommendation engine → outreach/interview generators → Streamlit dashboard + SQLite analytics + conversation feedback loop

## Tech Stack
Python, pandas, Streamlit, SQLite, pytest — no LLM API, no database complexity, no live scraping

## What It Proves
- Data engineering (pipeline, schema validation, SQL)
- Business analysis (requirements, risk register, case study)
- Explainable analytics (six-category scoring with rationale)
- Risk awareness (sponsorship disclaimers, noise detection)
- Business communication (outreach playbooks, interview packets)
- Systems thinking (recursive job search loop with portfolio feedback)

## Companion Projects
- **AI Agent Risk Scoring** — 8-category taxonomy, 0–100 rubric for LLM agent evaluation
- **Secure Cloud Evidence Lab** — IAM, SIEM, GRC synthetic artifacts for audit readiness

## Demo
```bash
streamlit run dashboard/app.py  →  http://localhost:8501
```

## Repo
https://github.com/abhishekyadav2000/career-intelligence-os

## Contact
Portfolio + demo available on request. Transparent about OPT/EAD work authorization.

---

*Portfolio demonstration project — MIT License.*
