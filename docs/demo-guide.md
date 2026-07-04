# Demo Guide — Career Intelligence OS

**Audience:** Recruiters, hiring managers, technical interviewers, portfolio reviewers  
**Positioning:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics  
**Run:** `streamlit run dashboard/app.py` → `http://localhost:8501`

---

## 2-Minute Demo Flow

| Step | Tab | What to Show | What It Proves |
|------|-----|--------------|----------------|
| 1 | **Overview** | KPI cards (50 companies, 117 jobs, 75 contacts), gap matrix P0 | Data pipeline + portfolio self-awareness |
| 2 | **Company Ranking** | Top 5 priority scores (JPMorgan, Goldman, Citi, etc.) | Enterprise targeting logic |
| 3 | **Recommendations** | Filter to "apply now" + "network first" | Decision automation with rationale |
| 4 | **Conversation Feedback** | Warm companies, objections, next actions | Closed-loop job search system |

**Closing line:** *"This is a sponsor-aware decision system — not a job board. It helps me prioritize, prepare, and iterate based on real conversations."*

---

## 5-Minute Demo Flow

| Step | Tab | Talking Point |
|------|-----|---------------|
| 1 | Overview | Universal profile + fit distribution — shows structured targeting |
| 2 | Company Ranking | Explain priority scoring: job count, contacts, sponsorship signal, DFW relevance |
| 3 | Role Fit | Drill into one high-fit role; show six-category breakdown |
| 4 | Sponsorship Signal | **Mandatory disclaimer** — signals only, verify via DOL/USCIS |
| 5 | Networking Map | Outreach angle for recruiter vs hiring manager |
| 6 | Interview Prep | Technical + business + behavioral topics mapped to job |
| 7 | Recommendations | Four actions: apply / network / research / skip |
| 8 | Export | CSV download + SQL demo query |
| 9 | Conversation Feedback | How interview insights feed back into portfolio gaps |

---

## What Each Tab Proves

| Tab | Employer Skill Signal |
|-----|----------------------|
| Overview | KPI storytelling, gap analysis |
| Company Ranking | Business prioritization, weighted scoring |
| Role Fit | Explainable analytics, keyword taxonomy |
| Sponsorship Signal | Risk-aware interpretation, compliance mindset |
| Networking Map | Business communication, stakeholder targeting |
| Interview Prep | Domain knowledge (cloud, security, data, AI) |
| Recommendations | Decision engine design |
| Export | SQL literacy, data export patterns |
| Conversation Feedback | Continuous improvement loop |

---

## Technical Q&A (Likely Questions)

**Q: Is this using an LLM API?**  
A: No. Scoring, outreach, and interview prep are rule-based Python modules. Prompt templates in `/prompts` show where LLM agents *would* plug in — deliberately deferred for portfolio clarity.

**Q: How do you validate sponsorship?**  
A: Heuristic signals from public notes and job text. Dashboard displays a disclaimer: verify via DOL/USCIS PERM and H-1B disclosure data. This is signal interpretation, not legal advice.

**Q: Where does the data come from?**  
A: Structured sample CSVs migrated from a DFW Top-50 sponsor-friendly employer workbook. No live scraping.

**Q: How is role fit calculated?**  
A: Six weighted categories against a universal enterprise technology profile: technical fit, business fit, sponsorship signal, DFW relevance, networking opportunity, noise risk.

**Q: What's the SQL demo?**  
A: SQLite audit trail with joins, aggregations, and CTEs — demonstrates analytics readiness without a production database.

**Q: How does Conversation Feedback work?**  
A: Rule-based analyzer on a conversation log CSV — detects warm companies, repeated objections, skill gaps, and next actions. No ML required.

---

## Sponsorship Disclaimer (Say This Out Loud)

> "Sponsorship signals in this dashboard are **indicative only** — derived from public employer notes and job text patterns. They are **not legal certainty**. Every role requires independent verification via DOL/USCIS disclosure data and direct recruiter confirmation. I am transparent about my OPT/EAD timeline when asked."

---

## Closing Script

> "Career Intelligence OS is my operating system for enterprise technology job search — not a résumé blaster. It combines data engineering, explainable scoring, sponsor-aware targeting, and a feedback loop from real conversations. The companion case studies cover AI agent risk scoring and cloud security evidence collection. Happy to walk through any module or share the GitHub repo."

---

## Pre-Demo Checklist

- [ ] Virtual env activated, dependencies installed
- [ ] `streamlit run dashboard/app.py` running
- [ ] Sidebar filters reset (all industries, all actions except skip)
- [ ] Conversation log has at least 3 sample rows
- [ ] GitHub repo link ready: https://github.com/abhishekyadav2000/career-intelligence-os
