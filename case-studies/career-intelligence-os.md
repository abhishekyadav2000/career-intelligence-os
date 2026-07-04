# Case Study: Career Intelligence OS

## Executive Summary

Career Intelligence OS is an AI-enabled enterprise decision system that helps analysts prioritize DFW technology employers, score role fit, interpret sponsorship signals, and plan outreach — demonstrating Python, SQL, data analytics, business analysis, and security/risk thinking in a single portfolio project.

## Business Problem

Enterprise technology hiring in DFW spans 50+ sponsor-friendly employers with overlapping role families. Candidates lack a structured system to answer: *Which companies first? Which roles fit? Are sponsorship signals reliable? Is this posting real? Should I apply or network?*

## Approach

Built a modular Python pipeline:

1. **Data layer** — Migrated DFW Top-50 workbook data into validated CSV schemas
2. **Scoring engine** — Six-category role fit scoring against universal profile
3. **Decision layer** — Actionable recommendations with rationale
4. **Communication layer** — Rule-based outreach and interview prep
5. **Dashboard** — Streamlit with 8 tabs, filters, and CSV export

## Results

| Metric | Value |
|--------|-------|
| Companies analyzed | 50 |
| Jobs scored | 117 |
| Contacts mapped | 75 |
| Scoring categories | 6 |
| Recommendation actions | 4 |
| Dashboard tabs | 8 |

## Technical Highlights

- Schema validation with duplicate and empty-row detection
- Weighted keyword scoring with explainable category breakdown
- Sponsorship signal heuristics with mandatory legal disclaimer
- Ghost job noise detection (template phrases, keyword stuffing)
- SQLite analytics demo with joins and aggregations
- Full test suite for scoring pipeline

## Skills Demonstrated

- Python data engineering (pandas, modular architecture)
- Business analysis (requirements, risk register, case study)
- Data analytics (scoring, KPIs, dashboard storytelling)
- Cloud/security domain knowledge (IAM, SIEM, GRC keyword taxonomy)
- AI automation thinking (prompt templates, rule-based agents)
- Risk awareness (sponsorship disclaimer, noise detection)

## Demo

```bash
streamlit run dashboard/app.py
```

## Future Enhancements

- LLM-powered company research agent
- Live DOL/USCIS data integration
- User accounts and saved search profiles
