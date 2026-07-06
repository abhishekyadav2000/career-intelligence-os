# Profile Intake Questionnaire

Use this form to populate `data/user_profile.yaml` or the **My Profile & Portfolio** tab in the dashboard. Replace every `[placeholder]` with your real details.

---

## Basics

| Field | What to provide | Example |
|-------|-----------------|---------|
| `name` | Your full name | `Abhishek Kumar` |
| `headline` | One-line professional identity | `Enterprise Technology Analyst — AI Automation & Cloud Security` |
| `positioning` | 2–3 sentences: who you are, what you deliver, for whom | `I build governed automation and cloud security evidence for regulated industries. My work connects data pipelines, IAM controls, and decision dashboards.` |
| `location` | Current metro / city | `DFW / Plano` |

---

## Target Career

| Field | What to provide | Example |
|-------|-----------------|---------|
| `target_roles` | Role families you want (not exact job titles) | `Technology Analyst`, `Cloud Security Analyst`, `Data Analyst`, `AI Automation Engineer` |
| `target_industries` | Industries to prioritize | `Financial Services`, `Healthcare`, `Telecom` |
| `target_locations` | Cities or remote preferences | `Plano`, `Dallas`, `Irving`, `Frisco`, `Remote DFW` |
| `years_experience` | Total years (including internships if relevant) | `2` |
| `career_goals` | What you're looking for in your next role | `Early-career analyst role where I can apply Python, SQL, and cloud security skills on production systems with mentorship.` |
| `deal_breakers` | Roles or conditions to avoid | `Pure sales`, `No sponsorship pathway`, `Fully on-site outside DFW` |
| `salary_expectation_range` | Optional range | `$75,000–$95,000` |
| `preferred_company_tiers` | Company types you prefer | `Tier 1 financial`, `Healthcare`, `Enterprise tech` |

---

## Work Authorization

| Field | What to provide | Example |
|-------|-----------------|---------|
| `authorization` | Visa / work status and pathway | `OPT/EAD authorized; STEM OPT extension eligible through 2028` |

---

## Education

| Field | What to provide | Example |
|-------|-----------------|---------|
| `education.school` | University name | `University of North Texas` |
| `education.degree` | Degree and major | `MS Information Systems` |
| `education.graduation` | Year or expected | `May 2026` |
| `education.relevant_coursework` | Courses that support target roles | `Database Systems`, `Cloud Computing`, `Information Security` |

---

## Skills & Tools

| Field | What to provide | Example |
|-------|-----------------|---------|
| `skills.technical` | Languages, frameworks, methods | `Python`, `SQL`, `REST APIs`, `ETL` |
| `skills.tools` | Platforms and software | `AWS`, `Tableau`, `Streamlit`, `Splunk`, `Git` |
| `skills.domains` | Subject-matter areas | `Cloud Security`, `GRC`, `AI Automation`, `Data Analytics` |
| `certifications` | Certs earned or in progress | `AWS Cloud Practitioner`, `CompTIA Security+` |

---

## Experience

| Field | What to provide | Example |
|-------|-----------------|---------|
| `experience_bullets` | Resume-style impact bullets (one per line) | `Built Career Intelligence OS — role-fit scoring dashboard (Streamlit + Python) with verified DFW employer data.` |

**Tip:** Start each bullet with a strong verb and include a measurable outcome where possible.

---

## Projects

Each project is an object with:

| Sub-field | Example |
|-----------|---------|
| `name` | `Career Intelligence OS` |
| `description` | `Sponsor-aware role-fit scoring and interview prep dashboard for DFW enterprise hiring.` |
| `skills` | `[Python, Streamlit, SQL]` |
| `url` | `https://github.com/you/career-intelligence-os` |

```yaml
projects:
  - name: Career Intelligence OS
    description: Role-fit scoring and interview prep dashboard.
    skills: [Python, Streamlit, SQL]
    url: https://github.com/you/repo
```

---

## Portfolio & Proof

| Field | What to provide | Example |
|-------|-----------------|---------|
| `portfolio_links` | Demo and case study links | `{title: "Cloud Evidence Lab", url: "case-studies/secure-cloud-evidence-lab.md"}` |
| `proof_asset_ids` | IDs from `data/proof_assets.csv` | `PA001`, `PA002`, `PA003` |

---

## STAR Stories (Behavioral Interviews)

Each story uses the STAR format:

| Sub-field | What to provide | Example |
|-----------|-----------------|---------|
| `id` | Short ID | `STAR001` |
| `title` | Story name | `Career Intelligence OS` |
| `situation` | Context | `Fragmented DFW hiring data across 50+ employers.` |
| `task` | Your responsibility | `Build a unified decision system for role fit and interview prep.` |
| `action` | What you did | `Designed CSV schema, scoring engine, and Streamlit dashboard.` |
| `result` | Outcome with metrics if possible | `Working demo with Mission Control and proof-matched outreach.` |
| `tags` | Keywords for matching questions | `[python, streamlit, data-analytics]` |

---

## Networking

| Field | What to provide | Example |
|-------|-----------------|---------|
| `networking_positioning` | How you want to be perceived in conversations | `I'm a builder who connects MIS, cloud security, and data automation — not a generic job seeker. I share proof, not pitches.` |

---

## Completeness Checklist

The dashboard shows a **Profile Completeness** score (0–100). Fields weighted most heavily for matching:

- [ ] **Target role families** — drives role fit board filtering
- [ ] **Technical skills** — drives profile match scoring
- [ ] **Experience bullets** — feeds interview simulator
- [ ] **STAR stories** — behavioral interview prep
- [ ] **Projects** — proof asset matching
- [ ] **Positioning statement** — outreach message drafts
- [ ] **Networking positioning** — engagement engine tone
- [ ] **Work authorization** — sponsorship-aware recommendations
- [ ] **Target locations** — DFW / remote scoring
- [ ] **Career goals** — recommendation context

**Minimum viable profile for matching:** name, headline, 5+ technical skills, 3+ target roles, 2+ experience bullets.

**Strong profile for Tier A matching:** all checklist items above plus 2+ STAR stories and 2+ projects with skill tags.

---

## How to Submit

1. **Dashboard:** Open **My Profile & Portfolio** → fill sections → **Save Profile**
2. **YAML:** Edit `data/user_profile.yaml` directly (see schema in repo root `data/`)
3. **Optional:** Add `data/uploads/resume_highlights.txt` for extra resume text (gitignored)

After saving, refresh **Demand First** and **Mission Control** to see profile-aware match scores.
