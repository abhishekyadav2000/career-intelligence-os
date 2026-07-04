"""Generate role_reasoning.csv rows for all jobs via rule-based inference."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data_loader import load_all

OUTPUT = ROOT / "data" / "role_reasoning.csv"

TEAM_MAP = {
    "security": "Security Engineering / Cloud Security",
    "cyber": "Cybersecurity Operations",
    "cloud": "Cloud Engineering / Platform",
    "data": "Data Analytics / Engineering",
    "automation": "AI/Automation COE",
    "risk": "Technology Risk / GRC",
    "operations": "Operations Technology",
    "network": "Network Operations / Infrastructure",
    "analyst": "Enterprise Technology / Business Analysis",
}

PROOF_MAP = {
    "security": "Show Secure Cloud Evidence Lab IAM/SIEM work; map controls to role requirements.",
    "cyber": "Connect cybersecurity case study and IAM work to enterprise security context.",
    "cloud": "Demonstrate cloud architecture patterns from Secure Cloud Evidence Lab.",
    "data": "Show Streamlit dashboard and SQL analytics from CI OS as live demo.",
    "automation": "Build governed automation prototypes; document control evidence.",
    "risk": "Apply AI Agent Risk Scoring framework to governance themes.",
    "python": "Apply Python/SQL pipeline patterns from portfolio projects.",
    "analytics": "Demonstrate KPI dashboard design and structured decision-making.",
}


def _infer_team(title: str, role_family: str) -> str:
    t = f"{title} {role_family}".lower()
    for keyword, team in TEAM_MAP.items():
        if keyword in t:
            return team
    return "Enterprise Technology"


def _infer_help(description: str, title: str) -> str:
    d = f"{description} {title}".lower()
    bullets = []
    for keyword, text in PROOF_MAP.items():
        if keyword in d and text not in bullets:
            bullets.append(text)
    if not bullets:
        bullets = [
            "Apply Python/SQL and cloud security skills from portfolio projects.",
            "Demonstrate structured decision-making via Career Intelligence OS.",
        ]
    return "; ".join(bullets[:3])


def _infer_questions(title: str, business_problem: str) -> str:
    t = title.lower()
    qs = []
    if "security" in t or "cyber" in t:
        qs.extend([
            "What cloud platforms dominate?",
            "How are incidents escalated?",
            "What compliance frameworks guide security decisions?",
        ])
    elif "data" in t or "analyst" in t:
        qs.extend([
            "What data platforms does the team use?",
            "How are analytics requests prioritized?",
            "What does success look like in the first 90 days?",
        ])
    elif "automation" in t or "ai" in t:
        qs.extend([
            "What automations are highest priority?",
            "How does the team measure AI governance?",
            "What tools are approved for workflow automation?",
        ])
    else:
        qs.extend([
            "What does success look like in the first 90 days?",
            "Which teams will I partner with most?",
            "What are the biggest current blockers?",
        ])
    if business_problem and len(qs) < 3:
        qs.append(f"How does the team address {business_problem[:60].lower()}?")
    return "; ".join(qs[:3])


def _metrics_for_team(team: str) -> tuple[str, str, str]:
    if "Security" in team or "Cyber" in team:
        return (
            "Complete security tooling onboarding; review IAM baselines.",
            "Tune SIEM detections; contribute to incident drill.",
            "Deliver control improvement with measurable risk reduction.",
        )
    if "Data" in team:
        return (
            "Learn data warehouse and metric definitions.",
            "Build dashboard or analysis for one product area.",
            "Present insights that influence a product or risk decision.",
        )
    if "Automation" in team or "AI" in team:
        return (
            "Learn automation toolchain and control requirements; deliver one pilot workflow.",
            "Ship two governed automations with audit evidence; partner on KPI dashboard.",
            "Present ROI summary and propose next automation backlog.",
        )
    return (
        "Learn team tools and deliver first small contribution.",
        "Own a workflow or analysis with documented outcomes.",
        "Present measurable improvement to stakeholders.",
    )


def generate_row(job: pd.Series, idx: int, profiles: pd.DataFrame) -> dict:
    title = str(job["title"])
    description = str(job.get("description", ""))
    visa_notes = str(job.get("visa_notes", ""))
    business_problem = (
        visa_notes.split("—")[0].strip()
        if "—" in visa_notes
        else visa_notes[:200]
    )
    company_id = job.get("company_id", "")
    profile_rows = profiles[profiles["company_id"] == company_id]
    industry = profile_rows.iloc[0]["industry"] if not profile_rows.empty else "Enterprise Technology"

    team = _infer_team(title, str(job.get("role_family", "")))
    m30, m60, m90 = _metrics_for_team(team)

    why = (
        f"{title} hiring supports {business_problem.lower()} "
        f"within {industry.lower()} organization."
    )

    return {
        "reasoning_id": f"RR{idx:03d}",
        "job_id": job["job_id"],
        "why_role_exists": why,
        "business_problem": business_problem,
        "likely_team": team,
        "success_metrics_30": m30,
        "success_metrics_60": m60,
        "success_metrics_90": m90,
        "how_i_would_help": _infer_help(description, title),
        "priority_questions": _infer_questions(title, business_problem),
    }


def main() -> int:
    data = load_all()
    jobs = data["jobs"]
    profiles = data["company_profiles"]

    existing = pd.read_csv(OUTPUT) if OUTPUT.exists() else pd.DataFrame()
    seeded = {row["job_id"]: row for _, row in existing.iterrows()} if not existing.empty else {}

    rows = []
    for i, (_, job) in enumerate(jobs.iterrows(), 1):
        if job["job_id"] in seeded:
            rows.append(seeded[job["job_id"]].to_dict())
        else:
            rows.append(generate_row(job, i, profiles))

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df)} role reasoning rows to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
