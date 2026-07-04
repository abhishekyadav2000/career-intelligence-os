"""One-time migration: legacy CSVs -> new sample_* schema."""

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

CAREER_URLS = {
    "JPMorgan Chase": "https://careers.jpmorgan.com",
    "Goldman Sachs": "https://www.goldmansachs.com/careers",
    "Bank of America": "https://careers.bankofamerica.com",
    "Citi": "https://jobs.citi.com",
    "Capital One": "https://www.capitalonecareers.com",
    "American Airlines": "https://jobs.aa.com",
    "AT&T": "https://www.att.jobs",
    "Charles Schwab": "https://www.schwabjobs.com",
    "Deloitte": "https://apply.deloitte.com",
    "NTT DATA": "https://careers.nttdata.com",
}


def slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("/", "-")[:40]


def migrate_companies() -> pd.DataFrame:
    old = pd.read_csv(DATA / "companies.csv")
    rows = []
    for _, r in old.iterrows():
        name = r["company_name"]
        rows.append({
            "company": name,
            "industry": r["industry"],
            "location": r["location"],
            "sponsor_signal": r.get("sponsor_signal", ""),
            "target_roles": "Technology Analyst; Cloud Security; Data Analytics; AI Automation",
            "career_url": CAREER_URLS.get(name, f"https://careers.example.com/{slug(name)}"),
            "notes": f"Rank {r.get('rank', '')}; {r.get('priority_tier', '')}; H1B confidence {r.get('h1b_confidence', '')}",
        })
    return pd.DataFrame(rows)


def migrate_jobs() -> pd.DataFrame:
    old = pd.read_csv(DATA / "jobs.csv")
    rows = []
    for i, r in old.iterrows():
        rows.append({
            "company": r["company_name"],
            "title": r["title"],
            "location": r["location"],
            "job_url": f"https://careers.example.com/{slug(r['company_name'])}/jobs/{r.get('job_id', i)}",
            "description": r["description"],
            "posted_date": f"2026-0{(i % 6) + 1}-{(i % 28) + 1:02d}",
            "role_family": r.get("role_cluster", "Enterprise Technology"),
            "visa_notes": f"{r.get('business_problem', '')} — validate sponsorship via DOL/USCIS; signal only, not legal certainty.",
        })
    return pd.DataFrame(rows)


def migrate_contacts() -> pd.DataFrame:
    old = pd.read_csv(DATA / "contacts.csv")
    angles = {
        "recruiter": "Lead with OPT/EAD status and role-fit proof",
        "hiring_manager": "Reference business problem and portfolio project",
        "peer": "Ask about day-to-day and team culture",
        "alumni": "Fellow alum connection and skills alignment",
    }
    rows = []
    for _, r in old.iterrows():
        ct = r.get("contact_type", "recruiter")
        rows.append({
            "company": r["company_name"],
            "contact_type": ct,
            "search_query": f"{r.get('persona', '')} {r.get('name', '')}".strip(),
            "LinkedIn_search_url": r.get("linkedin_search", ""),
            "message_angle": angles.get(ct, "Professional introduction with role-fit proof"),
            "notes": f"Status: {r.get('status', 'not_contacted')}; {r.get('priority_tier', '')}",
        })
    return pd.DataFrame(rows)


def migrate_profile_keywords() -> pd.DataFrame:
    return pd.DataFrame([
        {"skill": "AI automation", "category": "ai_automation", "weight": 0.15},
        {"skill": "cloud security", "category": "security", "weight": 0.15},
        {"skill": "data analytics", "category": "data_analytics", "weight": 0.12},
        {"skill": "GRC", "category": "risk_grc", "weight": 0.10},
        {"skill": "SQL", "category": "sql", "weight": 0.12},
        {"skill": "Python", "category": "python", "weight": 0.15},
        {"skill": "workflow automation", "category": "ai_automation", "weight": 0.11},
        {"skill": "cloud platforms", "category": "cloud", "weight": 0.10},
    ])


def main():
    migrate_companies().to_csv(DATA / "sample_companies.csv", index=False)
    migrate_jobs().to_csv(DATA / "sample_jobs.csv", index=False)
    migrate_contacts().to_csv(DATA / "sample_contacts.csv", index=False)
    migrate_profile_keywords().to_csv(DATA / "profile_keywords.csv", index=False)
    print("Migrated CSVs written to data/")


if __name__ == "__main__":
    main()
