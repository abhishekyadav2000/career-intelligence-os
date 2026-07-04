#!/usr/bin/env python3
"""Generate company-packets/*.md for all enriched companies."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PACKETS = ROOT / "company-packets"
sys.path.insert(0, str(ROOT))


def slug(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60]


def load_jobs_for_company(company_id: str) -> pd.DataFrame:
    jobs = pd.read_csv(DATA / "jobs.csv")
    return jobs[jobs["company_id"] == company_id].head(5)


def load_people(company_id: str) -> pd.DataFrame:
    people = pd.read_csv(DATA / "people_map.csv")
    return people[people["company_id"] == company_id]


def load_sources(company_id: str) -> pd.DataFrame:
    src = pd.read_csv(DATA / "research_sources.csv")
    return src[src["company_id"] == company_id]


def generate_packet(profile: pd.Series, companies: pd.DataFrame) -> str:
    cid = profile["company_id"]
    name = profile["company_name"]
    co_row = companies[companies["company_id"] == cid].iloc[0]
    rank = co_row.get("rank", "")
    jobs = load_jobs_for_company(cid)
    people = load_people(cid)
    sources = load_sources(cid)
    career = sources[sources["source_type"] == "careers_portal"]
    career_url = career.iloc[0]["source_url"] if not career.empty else ""

    job_lines = []
    for _, j in jobs.iterrows():
        job_lines.append(
            f"| {j['title']} | {j.get('location', '')} | {j.get('role_cluster', '')} | — |"
        )
    if not job_lines:
        job_lines.append("| Technology Analyst | DFW | Enterprise Technology | — |")

    contact_lines = []
    for _, p in people.iterrows():
        contact_lines.append(
            f"| {p['person_name']} | {p['role_title']} | {p['contact_type']} | {p['verification_status']} |"
        )

    source_lines = [f"- {u}" for u in str(profile.get("source_urls", "")).split(",") if u.strip()]
    for _, s in sources.head(5).iterrows():
        url = s["source_url"]
        if url not in str(profile.get("source_urls", "")):
            source_lines.append(f"- {url}")

    themes = str(profile.get("current_strategic_themes", profile.get("growth_signals", "")))
    tech = str(profile.get("technology_themes", profile.get("tech_stack_themes", "")))
    ai = str(profile.get("ai_data_cloud_security_themes", ""))

    return f"""# Company Packet: {name}

**Industry:** {profile['industry']}  
**Location:** {profile['dfw_presence']}  
**Career URL:** {career_url}  
**CI OS Priority Rank:** {rank} ({profile['priority_tier']})  
**Sponsorship Signal:** {profile.get('sponsorship_signal_summary', profile.get('sponsorship_context', ''))}

---

## Why This Company

{profile['strategic_summary']}

**Why they hire tech roles:** {profile.get('why_they_hire_tech_roles', '')}

**Business model:** {profile.get('business_model', '')}

---

## Target Roles (from job data)

| Title | Location | Role Family | Fit Score |
|-------|----------|-------------|-----------|
{chr(10).join(job_lines)}

---

## Talking Points

1. **Strategic themes:** {themes}
2. **Technology stack:** {tech}
3. **AI / cloud / security:** {ai}

---

## Outreach Angles

### Recruiter (via careers portal)
> Hi, I'm exploring {profile.get('common_role_families', 'technology analyst').split(';')[0].strip()} roles at {name}'s DFW locations. My portfolio includes a sponsor-aware Career Intelligence OS that scores enterprise role fit — demonstrating Python, SQL, and cloud security skills relevant to your teams. I'd welcome guidance on the best application path via your careers portal.

### Hiring Manager
> Hi, I'm targeting technology roles aligned with {themes.split(';')[0].strip() if themes else 'platform modernization'}. My portfolio includes a working Streamlit dashboard for role-fit scoring plus case studies on AI governance and cloud security evidence. I'd appreciate 15 minutes to learn about your team's current priorities.

---

## Interview Prep Topics

| Category | Likely Questions |
|----------|-----------------|
| Technical | Python, SQL, cloud platforms, IAM, SIEM, data pipelines |
| Business | Risk controls, stakeholder communication, KPI dashboards |
| Behavioral | Cross-functional collaboration, sponsorship transparency |

---

## Sponsorship Notes

- Signal: {profile.get('sponsorship_context', '')}
- Disclaimer: Indicative only — verify via DOL/USCIS PERM and H-1B disclosure data
- Not legal advice

---

## Contacts (public sources)

| Name | Title | Type | Verification |
|------|-------|------|--------------|
{chr(10).join(contact_lines) if contact_lines else '| Careers Recruiting Team | Technology Recruiting | recruiter | source_backed |'}

---

## Next Actions

- [ ] Review top-fit roles in Role Fit tab
- [ ] Apply via official careers portal
- [ ] Log conversations in conversation_log_template.csv

---

## Public Sources

{chr(10).join(source_lines[:8])}

**Last updated:** {profile.get('last_updated', '')}
"""


def main() -> int:
    profiles = pd.read_csv(DATA / "company_profiles.csv")
    companies = pd.read_csv(DATA / "companies.csv")
    PACKETS.mkdir(parents=True, exist_ok=True)

    for _, row in profiles.iterrows():
        content = generate_packet(row, companies)
        path = PACKETS / f"{slug(row['company_name'])}.md"
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path.name}")

    print(f"Generated {len(profiles)} company packets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
