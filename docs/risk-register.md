# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|----|------|-----------|--------|------------|-------|
| R-001 | Sponsorship signals misinterpreted as legal advice | Medium | High | Mandatory disclaimer on all outputs; docs/ai-safety-and-privacy.md | System |
| R-002 | Stale sample job data reduces demo credibility | Medium | Medium | Document data vintage; plan live feed for v2 | Data |
| R-003 | Ghost job detection false positives | High | Low | Label as heuristic; allow user override via filters | Scoring |
| R-004 | Keyword scoring misses nuanced role requirements | Medium | Medium | Six-category scoring with drill-down; gap analyzer | Scoring |
| R-005 | No authentication — not suitable for multi-user production | Low | Low | Explicitly out of MVP scope; document in README | Product |
| R-006 | SQLite DB regenerated on each load — no persistence | Low | Low | Document behavior; CSV export for persistence | Engineering |
| R-007 | Sample contact data uses placeholders | Low | Medium | Label as demo data; no real PII | Privacy |
| R-008 | Rule-based outreach may feel generic | Medium | Low | Personalization via matched skills and business problem | AI Layer |
| R-009 | scikit-learn imported but minimally used | Low | Low | Available for future ML models; rule-based for MVP | Engineering |
| R-010 | Dependency on manual CSV updates | Medium | Medium | Migration script; future API ingestion | Data |

## Review Schedule

- Review before each demo or presentation
- Update when new data sources or LLM agents are added
