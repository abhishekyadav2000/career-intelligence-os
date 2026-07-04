# Career Intelligence OS

**Enterprise job intelligence system for DFW sponsor-friendly targeting.**

Built from analysis of the DFW Top-50 Sponsor-Friendly Company Workbook, this project demonstrates Python, SQL, data analytics, AI automation, business analysis, and security/risk thinking in a single portfolio-ready application.

## Universal Profile

> Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics

## Features

| Feature | Module | What It Proves |
|---------|--------|----------------|
| CSV data loading | `src/loader.py` | Data engineering fundamentals |
| Keyword extraction | `src/keywords.py` | NLP-lite, taxonomy design |
| Role fit scoring | `src/scoring.py` | Weighted analytics, business logic |
| Outreach generation | `src/outreach.py` | Business communication, personalization |
| Interview prep | `src/interview.py` | Domain knowledge, structured thinking |
| SQLite analytics | `src/db.py` | SQL joins, aggregations, CTEs |
| Streamlit dashboard | `app/dashboard.py` | KPI storytelling, data visualization |

## Quick Start

```bash
# Clone and enter project
cd career-intelligence-os

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run app/dashboard.py
```

Open `http://localhost:8501` in your browser.

## Project Structure

```
career-intelligence-os/
├── README.md                 # This file
├── architecture.md           # System design
├── docs/case-study.md        # Recruiter-friendly case study
├── data/
│   ├── companies.csv         # 50 DFW target companies
│   ├── jobs.csv              # Sample job postings
│   ├── contacts.csv          # Networking contacts
│   └── gap_matrix.csv        # Portfolio capability gaps
├── src/
│   ├── loader.py             # CSV loading
│   ├── keywords.py           # Keyword extraction
│   ├── scoring.py            # Role fit scoring
│   ├── outreach.py           # Outreach angle generation
│   ├── interview.py            # Interview prep topics
│   └── db.py                 # SQLite analytics
└── app/
    └── dashboard.py          # Streamlit dashboard
```

## Gap Matrix Summary

Derived from the DFW Top-50 Universal Portfolio Sprint workbook `Capability_Matrix`:

| Priority | Capability | Career Intelligence OS Coverage |
|----------|-----------|--------------------------------|
| P0 | SQL + Python Data Automation | **Full** — parser, scoring, keywords |
| P0 | Dashboarding + KPI Storytelling | **Full** — Streamlit dashboard |
| P0 | AI Automation + RAG | **Partial** — rule-based intelligence pipeline |
| P0 | Enterprise Communication | **Partial** — outreach templates |
| P0 | Cloud / IAM / SIEM / GRC | **Referenced** — keyword matching, interview prep |
| P0 | AI Risk + Agentic Reliability | **Gap** — future project |
| P1 | Business Systems Analysis | **Partial** — pipeline workflow design |
| P1 | Agile + Delivery | **Gap** — backlog artifact not included |

## Target Role Mapping

This project maps to roles across all 50 DFW target companies:

- Technology Analyst
- Cloud Security Analyst
- Data Analyst
- AI Automation Analyst
- Technology Risk Analyst
- Cybersecurity Analyst
- Business Systems Analyst

**Highest-impact companies:** JPMorgan Chase, Citi, Capital One, Deloitte, NTT DATA, American Airlines, Charles Schwab, AT&T

## Data Sources

Sample data is derived from:
- `DFW_OPT_Sponsor_Targeting_Master_Workbook.xlsx` — 50 ranked companies, role clusters, keywords
- `DFW_Top50_Universal_Portfolio_Sprint.xlsx` — capability matrix, proof project specs

## Dashboard Tabs

1. **Overview** — KPIs, gap matrix, tier-1 companies, fit distribution
2. **Job Fit Scores** — weighted scoring with dimension breakdown
3. **Keywords** — extracted skills and category mapping
4. **Outreach** — personalized messages by contact type
5. **Interview Prep** — technical, business, and behavioral topics
6. **SQL Analytics** — demo queries on SQLite database

## License

MIT — portfolio demonstration project.
