# Case Study: Career Intelligence OS

## The Business Problem

Job searching across 50 DFW enterprise employers is inefficient without structure. The DFW OPT Sponsor Targeting Workbook identified 50 sponsor-friendly companies with recurring role families — but manually reading job descriptions, scoring fit, crafting outreach, and preparing for interviews across hundreds of roles is unsustainable.

**Core problem:** How do you turn a spreadsheet of target companies into an actionable, measurable job intelligence pipeline?

## Approach

I built Career Intelligence OS — a Python-based job intelligence system that:

1. **Ingests** structured company, job, and contact data from CSV
2. **Extracts** keywords from job descriptions using a skill taxonomy aligned to DFW enterprise hiring patterns
3. **Scores** role fit against a universal profile: *Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics*
4. **Generates** personalized outreach angles for recruiters, hiring managers, peers, and alumni
5. **Produces** interview prep topics mapped to matched skill categories
6. **Visualizes** everything in a Streamlit dashboard with SQLite analytics

## Architecture

```
CSV Data → Python Pipeline → SQLite → Streamlit Dashboard
                ↓
    Keywords → Scoring → Outreach + Interview Prep
```

**Key design decisions:**
- Rule-based (no API keys) for portfolio portability
- Weighted scoring mirrors the workbook's capability matrix priorities
- Template outreach follows the workbook's Outreach Playbook patterns
- SQLite demo proves SQL capability without external database setup

## Tools & Stack

| Layer | Technology |
|-------|-----------|
| Data | CSV, pandas, SQLite |
| Analysis | Python 3.10+, regex, collections.Counter |
| UI | Streamlit |
| Documentation | Markdown, Mermaid diagrams |

## Security & Risk Thinking

Even though this is a job-search tool, I applied enterprise security mindset:

- **No secrets in repo** — `.gitignore` blocks database and secrets files
- **Local-only data** — SQLite runs on-device, no cloud data exposure
- **Sample data only** — contact names are placeholders, not real PII
- **Audit trail design** — scoring breakdowns show exactly why a role matched (explainability)
- **Gap matrix** — explicitly documents what the project does NOT cover (AI risk scoring, GRC evidence packs)

## Data Workflow

1. Extracted 50 companies, role clusters, and keywords from DFW workbooks
2. Generated 117 sample jobs with realistic descriptions reflecting workbook patterns
3. Created 75 contacts across 4 persona types (recruiter, hiring manager, peer, alumni)
4. Built 12-row portfolio gap matrix from Capability_Matrix sheet

## Outcome Metrics

| Metric | Value |
|--------|-------|
| Companies loaded | 50 |
| Jobs analyzed | 117 |
| Contacts mapped | 75 |
| Avg role fit score | ~65–75 (Good Fit range) |
| Capability buckets covered | 8 of 12 (P0 partial-to-full) |
| SQL demo queries | 5 |
| Dashboard tabs | 6 |

## Portfolio Value

This single project demonstrates capabilities demanded across the DFW top-50:

| Capability | Proof |
|-----------|-------|
| Python | Full pipeline — loader, keywords, scoring, outreach, interview |
| SQL | SQLite schema, 5 analytical queries with joins and aggregations |
| Data Analytics | Weighted scoring, keyword frequency, KPI dashboard |
| AI Automation | Intelligent keyword extraction and automated outreach generation |
| Business Analysis | Outreach templates, business problem framing, gap matrix |
| Security/Risk | Skill taxonomy includes IAM/SIEM/GRC; gap matrix tracks security proof gaps |

## Interview Talking Points

1. **"Why this project?"** — "I analyzed 50 DFW sponsor-friendly companies and found the same 15 keywords in every job description. Instead of applying blindly, I built a system that scores fit and generates outreach — turning a spreadsheet into a pipeline."

2. **"How does scoring work?"** — "Weighted dimensions mirror enterprise hiring priorities: Python, SQL, cloud, security, data analytics, AI automation, risk/GRC, and business analysis. Each job gets a 0–100 score with a per-dimension breakdown."

3. **"What would you add next?"** — "RAG over my resume and project docs to answer 'why am I fit for this role?' — that's the P0 gap in my portfolio matrix. Also an AI Agent Risk Scoring Console for governance proof."

4. **"How is this secure?"** — "Local-only SQLite, no API keys, no real PII, explicit gap documentation for controls I haven't built yet. I think about what's provable, not just what's listed on a resume."

## Source Workbooks

- `DFW_OPT_Sponsor_Targeting_Master_Workbook.xlsx` — company rankings, role map, outreach playbook
- `DFW_Top50_Universal_Portfolio_Sprint.xlsx` — capability matrix, proof project specs, profile copy
