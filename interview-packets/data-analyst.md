# Interview Packet: Data Analyst

**Role Family:** Data Analyst  
**Universal Profile Fit:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics  
**Typical Employers:** Capital One, Charles Schwab, JPMorgan Chase, Citi, AT&T, Toyota

---

## Role Summary

Data analysts transform raw data into actionable insights — building pipelines, creating dashboards, running SQL queries, and communicating findings to stakeholders. Enterprise roles add compliance awareness, data governance, and KPI tracking at scale.

---

## Key Skills to Demonstrate

| Skill | Portfolio Evidence |
|-------|-------------------|
| SQL analytics | SQLite demo (joins, aggregations, CTEs) |
| Python data pipelines | `data_loader.py`, `data_cleaner.py`, pandas |
| Dashboard design | Streamlit Overview tab, fit distribution charts |
| KPI storytelling | Metric cards, company ranking, recommendations |
| Data validation | `schema_validator.py`, duplicate detection |
| Explainable scoring | Six-category role fit breakdown |

---

## Technical Questions (Prepare Answers)

1. **"Write a SQL query to find top companies by average fit score."**
   → Demo query in Export tab: `SELECT company, AVG(fit_score) ... GROUP BY company ORDER BY ...`

2. **"How do you ensure data quality?"**
   → Schema validation, duplicate detection, empty-row filtering, normalization in data_cleaner.

3. **"Describe your ETL process."**
   → CSV ingest → validate → clean → score → load to SQLite → dashboard display.

4. **"How would you visualize role fit distribution?"**
   → Bar chart by fit_label in Overview tab; category breakdown in Role Fit drill-down.

5. **"What's the difference between a KPI and a metric?"**
   → KPI = business outcome (companies prioritized, applications with high fit); metric = measurement (avg fit score, contact count).

---

## Business Questions

1. "How do you communicate findings to non-technical stakeholders?"
2. "Describe a dashboard you built and the decisions it enabled."
3. "How do you handle missing or dirty data?"
4. "What's your approach to defining success metrics for a new analysis?"

---

## Behavioral Questions (STAR Format)

| Question | Suggested Story Angle |
|----------|----------------------|
| Data-driven decision you made | Used scoring engine to prioritize top 5 companies vs. applying everywhere |
| Time data was wrong | Schema validator caught duplicates; fixed pipeline |
| Stakeholder wanted different metrics | Adjusted recommendation weights based on feedback |
| Most complex analysis | Six-category scoring with explainable breakdown |

---

## Questions to Ask Them

1. "What data sources does your team work with?"
2. "What BI tools does the team use (Tableau, Power BI, custom)?"
3. "How do you handle data governance and access controls?"
4. "What does the path from analysis to business action look like?"

---

## Portfolio Demo Path (3 min)

Overview (KPIs + fit distribution) → Role Fit drill-down → Export (SQL demo)

---

## Known Portfolio Gap

Conversation log flagged "SQL analytics case study depth" — prepare to walk through 2–3 queries live and explain query design choices.
