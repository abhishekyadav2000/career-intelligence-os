# Demand First Workflow

**Before people, find demand. Before outreach, find context. Before asking, create value.**

Career Intelligence OS v1.3 implements a 10-step operating model that starts with company activity — not LinkedIn people search.

---

## The 10 Steps

| Step | Action | Tool / Data | Output |
|------|--------|-------------|--------|
| 1. **Company** | Select Tier-1 target from ranked list | Company Ranking, `sample_companies.csv` | Focused company (Focus Mode ON) |
| 2. **Recent Jobs** | Review careers portal + demand signals | `company_demand_signals.csv`, careers URL | Source-backed hiring signals |
| 3. **Role Fit** | Score roles with 100-pt Demand First formula | `role_demand_scores.csv`, Demand First tab | Tier A/B/C/D board |
| 4. **Team Signals** | Identify business units and skills in demand | Demand signals by `technology_area` | Team hiring themes |
| 5. **People Map** | Build 15-slot contact pod with search URLs | `contact_pods.csv` | Verified or placeholder slots |
| 6. **Engagement Hook** | Match signal → hook → opener | `engagement_hooks.csv` | Level 1–10 engagement ladder |
| 7. **Message Draft** | Generate value-first copy (human review) | `outreach_queue.csv` | Draft messages — never auto-send |
| 8. **Manual Outreach** | Send after approval; log conversation | `conversation_log_template.csv` | Logged interaction |
| 9. **Feedback** | Analyze patterns; update portfolio | Conversation Feedback tab | Skill gaps, warm companies |
| 10. **Follow-up** | Tier A follow-up; iterate proof | Mission Control, pipeline cards | Stronger next cycle |

---

## Monday Workflow

### Morning (30 min) — Demand before People
1. Open **Execute → Demand First** with Focus Mode ON for target company
2. Review **Demand Signals** — confirm recent jobs, press, events (source links)
3. Check **Role Fit Board** — prioritize Tier A roles for outreach
4. Scan **Team Signals** — note business units hiring

### Midday (30 min) — Context before Outreach
5. Open **Contact Pod** — use search URLs to verify 1–2 contacts (no automation)
6. Pick an **Engagement Hook** aligned to a demand signal
7. Copy **Outreach Queue** draft; edit for authenticity; send manually
8. Log in `conversation_log_template.csv`

### Evening (20 min) — Proof loop
9. Review **Knowledge Graph** — Company → Role → Skill → Your Proof
10. Update portfolio artifact if feedback revealed a gap
11. Export Relationship Graph XLSX for weekly review

---

## Rules

- **No LinkedIn/Glassdoor scraping** — search URL templates only
- **Official/public sources** with `source_url` on every signal
- **Human-in-the-loop** for people selection and message sending
- **No fake names** — placeholders until `verified_public`
- **CSV-first** — works locally, no paid APIs

---

## Scoring (100 points)

| Dimension | Points |
|-----------|--------|
| DFW location | 20 |
| Posted last 14 days | 15 |
| MIS/cyber/cloud/data profile match | 25 |
| Early-career friendly (0–3 yrs) | 15 |
| Current skills match | 10 |
| Portfolio/cert support | 10 |
| Sponsor-friendly signal | 5 |

**Tiers:** A (75+), B (55–74), C (35–54), D (<35)

**Actions:** `immediate_outreach`, `apply_monitor`, `learning_stretch`, `ignore`

---

## Integration

| Component | Module |
|-----------|--------|
| Demand signals | `src/demand_intelligence_engine.py` |
| Role scoring | `src/role_demand_scorer.py` |
| Contact pods | `src/contact_pod_builder.py` |
| Engagement | `src/engagement_engine.py` |
| Knowledge graph | `src/knowledge_graph.py` |
| XLSX export | `src/relationship_workbook.py` |
| Mission Control priority | `src/mission_control_engine.py` |

Seed data: `python scripts/seed_demand_first_data.py`
