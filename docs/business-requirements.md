# Business Requirements

## BR-001: Data Ingestion
- System SHALL load companies, jobs, contacts, and profile keywords from CSV
- System SHALL validate schema (required columns, no empty keys, duplicate detection)
- System SHALL normalize company names, locations, titles, and role families

## BR-002: Role Fit Scoring
- System SHALL score each job against the universal enterprise technology profile
- System SHALL produce six category scores: technical fit, business fit, sponsorship signal, DFW relevance, networking opportunity, noise risk
- System SHALL assign fit labels: Strong Fit (≥75), Good Fit (≥55), Moderate Fit (≥35), Stretch Role (<35)

## BR-003: Company Prioritization
- System SHALL rank companies by composite priority score
- Priority SHALL consider tier, sponsorship signal, and pipeline depth (jobs + contacts)

## BR-004: Recommendations
- System SHALL recommend one of: apply now, network first, research more, skip/watchlist
- Each recommendation SHALL include composite score and rationale

## BR-005: Sponsorship Signals
- System SHALL surface H-1B/PERM keyword signals from company and job data
- All sponsorship outputs SHALL include legal disclaimer

## BR-006: Noise Detection
- System SHALL flag templated, short, or keyword-stuffed job descriptions
- High noise risk SHALL influence recommendation toward skip/watchlist

## BR-007: Outreach & Interview
- System SHALL generate outreach angles by contact type (recruiter, hiring manager, peer, alumni)
- System SHALL generate interview prep topics (technical, business, behavioral)

## BR-008: Dashboard
- System SHALL provide Streamlit dashboard with 8 tabs
- System SHALL support filtering by industry, company, and recommendation action
- System SHALL support CSV export of scores and recommendations

## BR-009: Audit Trail
- System SHALL initialize SQLite database from CSV data
- System SHALL provide demo SQL queries for analytics showcase

## Out of Scope (MVP)
- User authentication, payments, live job feeds, LinkedIn automation, LLM API integration
