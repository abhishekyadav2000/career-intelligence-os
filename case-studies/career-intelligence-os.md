# Case Study: Career Intelligence OS

## 1. Executive Summary

Career Intelligence OS is an AI-enabled enterprise decision system that helps analysts prioritize DFW technology employers, score role fit against a universal enterprise technology profile, interpret sponsorship signals responsibly, and plan outreach and interview preparation — all in a single portfolio project that demonstrates Python, SQL, data analytics, business analysis, and security/risk thinking.

**Universal Profile:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics

| Metric | Value |
|--------|-------|
| Companies analyzed | 50 |
| Jobs scored | 117 |
| Contacts mapped | 75 |
| Scoring categories | 6 |
| Recommendation actions | 4 |
| Dashboard tabs | 9 (8 core + Conversation Feedback) |

---

## 2. Business Problem

Enterprise technology hiring in the Dallas–Fort Worth metro spans 50+ sponsor-friendly employers with overlapping role families — business systems analyst, data analyst, cybersecurity, cloud security, AI automation, and technical project coordinator. Candidates and early-career analysts lack a structured system to answer:

- **Which companies first?** — Priority ranking across finance, telecom, automotive, and consulting sectors
- **Which roles fit?** — Multi-dimensional scoring against a defined profile
- **Are sponsorship signals reliable?** — Heuristic interpretation with mandatory legal disclaimers
- **Is this posting real?** — Ghost job and noise detection
- **Should I apply or network?** — Four-action recommendation engine
- **What do I say in outreach?** — Rule-based angle generation by contact type
- **How do I prepare for interviews?** — Technical, business, and behavioral topic mapping
- **What did I learn from conversations?** — Feedback loop into portfolio gaps

Without this system, job search becomes reactive résumé blasting rather than a measurable decision process.

---

## 3. Stakeholders

| Stakeholder | Need | How CI OS Addresses It |
|-------------|------|------------------------|
| **Candidate (primary user)** | Prioritize effort, prepare conversations | Dashboard, packets, playbooks |
| **Recruiter** | Evidence of structured thinking | Demo guide, portfolio narrative |
| **Hiring manager** | Role-fit rationale, domain knowledge | Scoring breakdown, interview prep |
| **Portfolio reviewer** | Working demo + business case | Streamlit app + case study |
| **Compliance / risk** | Sponsorship signal handling | Disclaimers, signal-only interpretation |

---

## 4. Requirements

### Functional
- Ingest structured CSV data (companies, jobs, contacts, gap matrix)
- Score roles across six categories with explainable breakdown
- Rank companies by composite priority
- Generate four recommendation actions with rationale
- Produce outreach angles by contact type (recruiter, hiring manager, peer, alumni)
- Map interview topics (technical, business, behavioral) per job
- Export scores and recommendations as CSV
- Run SQL analytics demo against SQLite audit trail
- Analyze conversation log for warm companies, objections, and portfolio gaps

### Non-Functional
- No login, no production database, no LLM API dependency
- Sponsor-aware with transparent OPT/EAD disclosure guidance
- Portfolio-grade documentation and demo scripts
- Test coverage for scoring and feedback modules

---

## 5. Approach

Built a modular Python pipeline in five layers:

1. **Data layer** — Migrated DFW Top-50 workbook into validated CSV schemas with schema validation and duplicate detection
2. **Scoring engine** — Six-category role fit scoring against universal profile with weighted keyword taxonomy
3. **Decision layer** — Company priority scoring and four-action recommendation engine
4. **Communication layer** — Rule-based outreach angle and interview topic generators
5. **Presentation layer** — Streamlit dashboard with filters, drill-down, export, and conversation feedback loop

Design principle: **explainable over opaque**. Every score, recommendation, and outreach angle includes rationale.

---

## 6. Architecture

```
data/ (CSVs)
    ↓
data_loader → schema_validator → data_cleaner
    ↓
scoring engine
  ├── role_fit_scorer (6 categories)
  ├── company_priority_scorer
  ├── sponsorship_signal (disclaimer-enforced)
  └── noise_detector
    ↓
recommendation_engine
    ↓
communication generators
  ├── outreach_angle_generator
  ├── interview_topic_mapper
  └── profile_gap_analyzer
    ↓
dashboard/app.py (Streamlit)
  ├── 8 analysis tabs
  ├── Export + SQL demo
  └── Conversation Feedback (conversation_feedback_analyzer)
    ↓
SQLite audit trail (demo queries)
```

See [docs/architecture.md](../docs/architecture.md) for full system design.

---

## 7. Data Model

| Dataset | Records | Key Fields |
|---------|---------|------------|
| `sample_companies.csv` | 50 | company, industry, location, sponsor_signal, target_roles |
| `sample_jobs.csv` | 117 | company, title, description, role_family, visa_notes |
| `sample_contacts.csv` | 75 | company, contact_type, name, title, linkedin_url |
| `profile_keywords.csv` | — | Skill taxonomy for scoring |
| `conversation_log_template.csv` | 5 sample | Outreach/interview feedback loop |

Schema validation enforces required columns, detects duplicates, and normalizes text fields before scoring.

---

## 8. Scoring Methodology

### Role Fit — Six Categories

| Category | Weight Logic | What It Measures |
|----------|-------------|------------------|
| Technical fit | Keyword coverage across Python, SQL, cloud, security, data, AI | Hard skills match |
| Business fit | Business analysis + risk/GRC keywords | Stakeholder and controls literacy |
| Sponsorship signal | Visa note patterns + employer history notes | Sponsor likelihood (signal only) |
| DFW relevance | Location match to Dallas/Plano/Irving/Fort Worth | Geographic targeting |
| Networking opportunity | Contact count and type diversity | Warm intro potential |
| Noise risk | Ghost job heuristics (template phrases, keyword stuffing) | Posting quality |

### Company Priority

Composite of job count, contact count, average fit score, sponsorship signal, and industry tier.

### Recommendations — Four Actions

| Action | Trigger Pattern |
|--------|----------------|
| Apply now | High fit + low noise + strong sponsorship signal |
| Network first | Good fit + contacts available + moderate sponsorship |
| Research more | Unclear fit or weak sponsorship signal |
| Skip / watchlist | Low fit or high noise risk |

---

## 9. Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Companies analyzed | 50 | Full DFW Top-50 coverage |
| Jobs scored | 117 | ~2.3 roles per company average |
| Contacts mapped | 75 | ~1.5 contacts per company |
| Scoring categories | 6 | Explainable multi-dimensional fit |
| Recommendation actions | 4 | Clear decision taxonomy |
| Dashboard tabs | 9 | End-to-end workflow coverage |
| Test suite | 2 modules | Scoring + conversation feedback |

Top-priority companies in sample data: JPMorgan Chase, Goldman Sachs, Bank of America, Citi, Charles Schwab, Capital One — consistent with DFW finance-tech hiring concentration.

---

## 10. Technical Highlights

- **Schema validation** with duplicate and empty-row detection (`schema_validator.py`)
- **Weighted keyword scoring** with explainable category breakdown (`keyword_extractor.py`, `role_fit_scorer.py`)
- **Sponsorship signal heuristics** with mandatory legal disclaimer (`sponsorship_signal.py`)
- **Ghost job noise detection** — template phrases, keyword stuffing flags (`noise_detector.py`)
- **SQLite analytics demo** with joins, aggregations, and CTEs (`db.py`)
- **Conversation feedback analyzer** — rule-based objection and gap detection (`conversation_feedback_analyzer.py`)
- **Full test suite** for scoring pipeline and feedback loop (`tests/`)

---

## 11. Skills Demonstrated

| Skill Domain | Evidence |
|-------------|----------|
| Python data engineering | Modular `src/` architecture, pandas pipelines |
| Business analysis | Requirements doc, risk register, case study |
| Data analytics | Scoring engine, KPI dashboard, SQL demo |
| Cloud/security domain | IAM, SIEM, GRC keyword taxonomy |
| AI automation thinking | Prompt templates, agent risk scoring companion case study |
| Risk awareness | Sponsorship disclaimer, noise detection, governance hooks |
| Business communication | Outreach playbooks, interview packets, company packets |
| Systems thinking | Recursive job search loop with feedback into portfolio |

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sponsorship signal misinterpreted as legal certainty | Compliance / trust | Mandatory disclaimer on every sponsorship view |
| Stale sample data | Outdated targeting | Documented as portfolio sample; live scraping deferred |
| Over-reliance on keyword matching | False fit scores | Six-category breakdown + manual drill-down |
| Ghost job false negatives | Wasted applications | Noise risk category + "research more" action |
| Conversation log not maintained | Feedback loop breaks | Template CSV with sample rows + dashboard guidance |

See [docs/risk-register.md](../docs/risk-register.md) for full register.

---

## 13. Demo

```bash
git clone https://github.com/abhishekyadav2000/career-intelligence-os.git
cd career-intelligence-os
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Open `http://localhost:8501`. See [docs/demo-guide.md](../docs/demo-guide.md) for 2-min and 5-min demo flows.

**Dashboard screenshots:** [screenshots/](../screenshots/)

---

## 14. Future Enhancements

- LLM-powered company research agent (prompt templates ready in `/prompts`)
- Live DOL/USCIS H-1B and PERM data integration
- User accounts and saved search profiles
- AI Agent Risk Scoring module (companion case study)
- Secure Cloud Evidence Lab integration (companion case study)
- Automated conversation log import from LinkedIn/email exports

---

## Companion Projects

| Case Study | Connection |
|-----------|------------|
| [AI Agent Risk Scoring](ai-agent-risk-scoring.md) | Gap matrix P0 — agentic reliability |
| [Secure Cloud Evidence Lab](secure-cloud-evidence-lab.md) | Gap matrix P0 — IAM/SIEM/GRC evidence |

## License

MIT — portfolio demonstration project.
