# System Design One-Pager

## Career Intelligence OS

**Tagline:** Sponsor-aware career intelligence system for enterprise technology roles.

## Problem
DFW enterprise technology hiring is fragmented. Candidates lack a decision system for role fit, sponsorship signals, and outreach strategy.

## Solution
Python-based intelligence pipeline: CSV → validate → score → recommend → dashboard.

## Key Components

| Component | Purpose |
|-----------|---------|
| Data Layer | 50 companies, 117 jobs, 75 contacts (CSV + validation) |
| Scoring Engine | 6-category role fit + company priority + noise detection |
| Decision Layer | apply / network / research / skip recommendations |
| Communication | Outreach angles + interview prep + gap analysis |
| Dashboard | Streamlit with 8 tabs, filters, CSV export |
| Audit | SQLite demo with 5 analytics queries |

## Architecture Pattern
Modular Python pipeline with thin backward-compatibility wrappers. Rule-based intelligence (no LLM API in MVP). Prompt templates ready for future AI agents.

## Tech Stack
Python 3.12, pandas, Streamlit, SQLite, scikit-learn, Plotly

## Proof Triangle
1. **Working Demo** — `streamlit run dashboard/app.py`
2. **Business Case** — case-studies/, docs/business-requirements.md, docs/risk-register.md
3. **Conversation Weapon** — presentation/demo-script.md

## Run
```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Deferred
Login, payments, live feeds, LinkedIn automation, LLM APIs, mobile app
