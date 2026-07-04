# Career Intelligence OS

**Sponsor-aware career intelligence system for enterprise technology roles.**

An AI-enabled enterprise decision system for role-fit scoring, talent intelligence, outreach strategy, sponsor-aware targeting, and interview readiness — built as a portfolio proof triangle: working demo, business case, and conversation weapon.

> **Universal Profile:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics

## Business Problem

Enterprise technology hiring in DFW is fragmented across 50+ sponsor-friendly employers, hundreds of role families, and opaque sponsorship signals. Candidates and analysts lack a unified decision system to prioritize companies, score role fit, detect noise, and plan outreach — leading to wasted applications and missed warm-intro opportunities.

## Solution

Career Intelligence OS ingests structured company, job, and contact data; scores roles against a universal enterprise technology profile; surfaces sponsorship signals (with legal disclaimers); and generates actionable recommendations — apply now, network first, research more, or skip/watchlist.

## Features

| Capability | Module | What It Proves |
|------------|--------|----------------|
| Data ingestion & validation | `src/data_loader.py`, `src/schema_validator.py` | Data engineering, schema design |
| Role-fit scoring | `src/role_fit_scorer.py` | Weighted analytics, business logic |
| Company prioritization | `src/company_priority_scorer.py` | Enterprise targeting decisions |
| Sponsorship signals | `src/sponsorship_signal.py` | Risk-aware signal interpretation |
| Noise detection | `src/noise_detector.py` | Quality heuristics, ghost job flags |
| Recommendations | `src/recommendation_engine.py` | Decision automation |
| Outreach angles | `src/outreach_angle_generator.py` | Business communication |
| Interview prep | `src/interview_topic_mapper.py` | Domain knowledge mapping |
| Gap analysis | `src/profile_gap_analyzer.py` | Skills gap identification |
| Dashboard | `dashboard/app.py` | KPI storytelling, Streamlit |

## Quick Start

```bash
git clone https://github.com/abhishekyadav2000/career-intelligence-os.git
cd career-intelligence-os
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Open `http://localhost:8501`.

## Demo Flow

1. **Overview** — KPIs, gap matrix, fit distribution
2. **Company Ranking** — priority scores across 50 DFW targets
3. **Role Fit** — six-category scoring with drill-down
4. **Sponsorship Signal** — H-1B/PERM indicators (signal only)
5. **Networking Map** — outreach angles by contact type
6. **Interview Prep** — technical, business, behavioral topics
7. **Recommendations** — apply / network / research / skip
8. **Export** — CSV download + SQL analytics demo
9. **Conversation Feedback** — outreach insights, warm companies, portfolio gaps

See [docs/demo-guide.md](docs/demo-guide.md) for 2-min and 5-min demo scripts.

## Dashboard Walkthrough

| # | Tab | Screenshot |
|---|-----|------------|
| 1 | Overview | ![Overview](screenshots/01-overview-dashboard.png) |
| 2 | Company Ranking | ![Company Ranking](screenshots/02-company-ranking.png) |
| 3 | Role Fit | ![Role Fit](screenshots/03-role-fit.png) |
| 4 | Sponsorship Signal | ![Sponsorship Signal](screenshots/04-sponsorship-signal.png) |
| 5 | Networking Map | ![Networking Map](screenshots/05-networking-map.png) |
| 6 | Interview Prep | ![Interview Prep](screenshots/06-interview-prep.png) |
| 7 | Recommendations | ![Recommendations](screenshots/07-recommendations.png) |
| 8 | Export & SQL | ![Export](screenshots/08-export-sql-demo.png) |

To recapture screenshots: `python scripts/capture_screenshots.py` (requires Playwright + running dashboard).

## Architecture

```
data/ (CSVs) → data_loader → schema_validator → data_cleaner
                                    ↓
              scoring engine (role_fit, company_priority, sponsorship, noise)
                                    ↓
              recommendation_engine → outreach / interview / gap analyzers
                                    ↓
              dashboard/app.py (Streamlit) + SQLite audit trail
```

See [docs/architecture.md](docs/architecture.md) for full system design.

## Project Structure

```
career-intelligence-os/
├── src/                    # Python modules
├── data/                   # Sample datasets + conversation log
├── dashboard/              # Streamlit app
├── docs/                   # Architecture, vision, demo guide, job search loop
├── case-studies/           # Portfolio case studies (3)
├── company-packets/        # Target company briefs (5 + template)
├── conversation-playbooks/ # Outreach scripts (6 playbooks)
├── interview-packets/      # Role family prep (6 packets)
├── prompts/                # AI agent prompt templates
├── presentation/           # Demo scripts, LinkedIn copy, walkthrough
├── tests/                  # Scoring + conversation feedback tests
├── screenshots/            # Dashboard captures
├── scripts/                # Screenshot capture utility
├── README.md
├── requirements.txt
└── .env.example
```

## Employer Proof Points

- **Data pipeline:** CSV ingestion with schema validation and normalization
- **Decision engine:** Multi-dimensional scoring with explainable categories
- **Risk awareness:** Sponsorship signals flagged as indicative, not legal certainty
- **Business communication:** Rule-based outreach and interview prep generators
- **SQL analytics:** SQLite demo with joins, aggregations, CTEs
- **Portfolio narrative:** Case study, architecture docs, demo scripts

## Tests

```bash
python3 tests/test_scoring.py
# or
python3 -m pytest tests/
```

## Data

Sample data migrated from DFW Top-50 Sponsor-Friendly Company Workbook:
- 50 companies, ~117 jobs, ~75 contacts
- See [docs/data-dictionary.md](docs/data-dictionary.md)

## License

MIT — portfolio demonstration project.
