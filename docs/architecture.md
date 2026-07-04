# Architecture

## System Overview

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  data/      │───▶│  data_loader     │───▶│  schema_validator   │
│  CSVs       │    │  data_cleaner    │    │  (quality gates)    │
└─────────────┘    └──────────────────┘    └─────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │       Scoring Engine        │
              │  role_fit_scorer            │
              │  company_priority_scorer    │
              │  sponsorship_signal         │
              │  noise_detector             │
              └─────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │   recommendation_engine     │
              │   outreach_angle_generator  │
              │   interview_topic_mapper    │
              │   profile_gap_analyzer      │
              └─────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    ┌──────────────────┐        ┌──────────────────┐
    │ dashboard/app.py │        │ SQLite audit DB  │
    │ (Streamlit)      │        │ (SQL demo)       │
    └──────────────────┘        └──────────────────┘
```

## Layers

### 1. Data Ingestion
- **Source:** CSV files in `data/` (companies, jobs, contacts, profile keywords)
- **Loader:** `src/data_loader.py` — reads, validates, cleans, enriches with IDs
- **Validator:** `src/schema_validator.py` — missing columns, empty rows, duplicates
- **Cleaner:** `src/data_cleaner.py` — normalize names, locations, titles, role families

### 2. Scoring Engine
- **Role Fit:** `src/role_fit_scorer.py` — weighted keyword matching against universal profile
- **Categories:** technical fit, business fit, sponsorship signal, DFW relevance, networking opportunity, noise risk
- **Company Priority:** `src/company_priority_scorer.py` — tier, sponsor signal, pipeline depth
- **Sponsorship:** `src/sponsorship_signal.py` — H-1B/PERM keyword signals (not legal certainty)
- **Noise:** `src/noise_detector.py` — ghost job heuristics

### 3. AI Layer (MVP: Rule-Based + Prompts)
- Rule-based outreach, interview, and gap generators
- Prompt templates in `prompts/` for future LLM agent integration
- No external LLM API calls in MVP

### 4. Dashboard
- **Streamlit app:** `dashboard/app.py`
- Tabs: overview, company ranking, role fit, sponsorship, networking, interview prep, recommendations, export
- Filters: industry, company, recommendation action
- CSV export for scores and recommendations

### 5. Audit Trail
- **SQLite:** `src/db.py` — auto-initialized from CSV on dashboard load
- Demo queries: jobs by tier, top companies, contacts by type, tier-1 pipeline, industry breakdown

### 6. Privacy
- No PII stored beyond sample contact placeholders
- No external API calls in MVP
- Sponsorship signals include mandatory disclaimer
- See [ai-safety-and-privacy.md](ai-safety-and-privacy.md)

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12+ |
| Data | pandas, CSV |
| Scoring | scikit-learn (available), rule-based heuristics |
| Dashboard | Streamlit, Plotly |
| Analytics DB | SQLite |
| Config | python-dotenv, `.env.example` |
| Tests | pytest |

## Deployment (Future)

- Streamlit Cloud or Docker container
- Environment variables via `.env`
- No authentication in MVP
