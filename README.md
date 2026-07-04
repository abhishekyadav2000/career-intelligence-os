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
| **Interview Command Center** | `src/company_profile_engine.py`, `src/conversation_brief_generator.py`, etc. | End-to-end interview prep with company 360, people map, role reasoning, proof matching |

## Interview Command Center

The ICC upgrade transforms CI OS from a portfolio dashboard into an **end-to-end interview preparation system**:

| Capability | Module | Data File |
|------------|--------|-----------|
| Company 360 profiles | `src/company_profile_engine.py` | `data/company_profiles.csv` |
| People / power mapping | `src/people_power_mapper.py` | `data/people_map.csv` |
| Role reasoning (30/60/90) | `src/role_reasoning_engine.py` | `data/role_reasoning.csv` |
| Proof-of-work matching | `src/proof_asset_mapper.py` | `data/proof_assets.csv` |
| Conversation briefs | `src/conversation_brief_generator.py` | `data/conversation_briefs.csv` |
| Research prompts | `src/research_prompt_generator.py` | `prompts/*.md` |

**Seed companies:** JPMorgan Chase, Citi, Capital One, Toyota Motor North America, AT&T

**Rules:** CSV-first, TBD placeholders with `verification_status`, no scraping/automation, no fake names.

### ICC Demo Flow

1. Open dashboard → global selectors at top: company, role, conversation type, stage
2. **Interview Command Center** tab → click **Generate Brief**
3. Review 7 sections: Company 360, Role Intelligence, People Map, Proof Match, Script, Interview Prep, Action Plan
4. **Export Brief as Markdown** or **Save Brief** (appends to CSV + `exports/`)
5. Explore **Company 360**, **People Map**, **Role Deep Dive**, **Proof Assets** tabs
6. Use research prompt expanders to enrich CSVs manually (see [docs/research-enrichment-workflow.md](docs/research-enrichment-workflow.md))

**Acceptance test:** JPMorgan Chase + any role + hiring manager + hiring manager screen → full brief + markdown export.

| # | Tab | Screenshot |
|---|-----|------------|
| 0 | Interview Command Center | ![ICC](screenshots/09-interview-command-center.png) |
| 1 | Company 360 | ![Company 360](screenshots/10-company-360.png) |
| 2 | People Map | ![People Map](screenshots/11-people-map.png) |
| 3 | Role Deep Dive | ![Role Deep Dive](screenshots/12-role-deep-dive.png) |
| 4 | Proof Assets | ![Proof Assets](screenshots/13-proof-assets.png) |


```bash
git clone https://github.com/abhishekyadav2000/career-intelligence-os.git
cd career-intelligence-os
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Open `http://localhost:8501`.

## Demo Flow

1. **Interview Command Center** — generate full conversation brief (start here)
2. **Overview** — KPIs, gap matrix, fit distribution
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
├── src/                    # Python modules (scoring + ICC engines)
├── data/                   # Sample datasets + ICC CSVs + conversation log
├── dashboard/              # Streamlit app
├── docs/                   # Architecture, vision, demo guide, job search loop
├── case-studies/           # Portfolio case studies (3)
├── company-packets/        # Target company briefs (5 + template)
├── conversation-playbooks/ # Outreach scripts (6 playbooks)
├── interview-packets/      # Role family prep (6 packets)
├── prompts/                # AI agent prompt templates
├── presentation/           # Demo scripts, LinkedIn copy, walkthrough
├── tests/                  # Scoring + ICC + conversation feedback tests
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
