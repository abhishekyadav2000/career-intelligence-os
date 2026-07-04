# Research Enrichment Workflow

Manual, CSV-first workflow for enriching Interview Command Center data without scraping, LinkedIn automation, or paid APIs.

## Principles

1. **Public sources only** — careers portals, earnings themes, industry reports, DOL/USCIS
2. **TBD placeholders** — never invent contact names; use `verification_status`
3. **Confidence levels** — high / medium / low for project themes
4. **CSV as source of truth** — all enrichment lands in `data/*.csv`

## Workflow Steps

### 1. Company Profile Enrichment

**Input:** `data/company_profiles.csv`, `data/company_projects.csv`, `data/research_sources.csv`

1. Open **Company 360** tab → select target company
2. Review **Research Gaps** section
3. Copy **Company Deep Profile Research Prompt** from expander
4. Run prompt in Claude or Deep Research (manual)
5. Validate claims against public URLs
6. Update CSV rows with verified data
7. Set `last_updated` on company profile

**Output files:** `company_profiles.csv`, `company_projects.csv`, `research_sources.csv`

### 2. People Map Enrichment

**Input:** `data/people_map.csv`

1. Open **People Map** tab
2. Use **Search Query URLs** to manually verify contacts on LinkedIn
3. Until verified, keep `person_name` as `TBD Recruiter`, `TBD Hiring Manager`, etc.
4. Update `verification_status`: `placeholder` → `partial` → `verified`
5. Adjust `hiring_power_score` based on relevance

**Never:** automate LinkedIn searches, scrape profiles, or use fake names.

### 3. Role Reasoning Enrichment

**Input:** `data/role_reasoning.csv`, `data/sample_jobs.csv`

1. Open **Role Deep Dive** tab → select role
2. Copy **Role Reasoning Research Prompt**
3. Analyze JD for business problem and 30/60/90 metrics
4. Add/update row in `role_reasoning.csv` linked to `job_id`

### 4. Proof Asset Mapping

**Input:** `data/proof_assets.csv`

1. Open **Proof Assets** tab
2. Review **Missing Proof Gaps**
3. Add new assets (case studies, screenshots, packets) to repo
4. Register in `proof_assets.csv` with tags matching role/company themes

### 5. Conversation Brief Generation

**Input:** All enriched CSVs

1. Open **Interview Command Center** tab
2. Select company, role, conversation type, interview stage
3. Click **Generate Brief**
4. Review all 7 sections
5. **Save Brief** → appends to `conversation_briefs.csv` + exports markdown to `exports/`
6. **Export Brief as Markdown** for interview prep

## File Reference

| File | Purpose |
|------|---------|
| `company_profiles.csv` | Strategic 360 profiles for ICC seed companies |
| `people_map.csv` | TBD contact placeholders with search URLs |
| `company_projects.csv` | Public initiative themes with confidence |
| `role_reasoning.csv` | Why role exists, 30/60/90, questions |
| `proof_assets.csv` | Portfolio artifacts for proof-of-work matching |
| `conversation_briefs.csv` | Saved brief metadata |
| `research_sources.csv` | Public source URLs with verification status |

## Agent Prompts

See `prompts/` directory:

- `company-deep-profile-agent.md`
- `people-map-agent.md`
- `role-reasoning-agent.md`
- `conversation-brief-agent.md`

## Acceptance Test

1. Select **JPMorgan Chase** + any role + **hiring manager** + **hiring manager screen**
2. Click **Generate Brief**
3. Verify all 7 sections populate
4. Export markdown — confirm Company 360, Role Intelligence, People Map, Proof Match, Script, Interview Prep, Action Plan

## Refresh Cadence

- **Weekly:** Check careers portals for new roles
- **Before interview:** Regenerate brief with updated conversation type/stage
- **After conversation:** Log insights in `conversation_log_template.csv`
