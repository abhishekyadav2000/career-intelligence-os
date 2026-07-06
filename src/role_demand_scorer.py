"""Role demand scoring — 100-point Demand First formula (v1.3)."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import pandas as pd

from src.keyword_extractor import categorize_keywords

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ROLE_DEMAND_SCORES_PATH = DATA_DIR / "role_demand_scores.csv"

PROFILE_ROLE_FAMILIES = {
    "mis",
    "cyber",
    "cloud",
    "data",
    "security",
    "analyst",
    "automation",
    "ai",
}

EARLY_CAREER_TERMS = (
    "analyst",
    "associate",
    "early career",
    "0-3",
    "graduate",
    "intern",
    "entry",
    "junior",
    "development program",
)

DFW_TERMS = ("dallas", "plano", "irving", "fort worth", "dfw", "westlake")

ROLE_DEMAND_COLUMNS = [
    "job_id",
    "company_id",
    "company_name",
    "job_title",
    "role_family",
    "posted_date",
    "location",
    "dfw_score",
    "recency_score",
    "profile_match_score",
    "early_career_score",
    "skills_match_score",
    "portfolio_support_score",
    "sponsor_score",
    "total_fit_score",
    "fit_tier",
    "recommended_action",
    "source_url",
    "last_scored",
]


def _parse_date(value: str) -> datetime | None:
    if not value or str(value).strip() in ("", "nan"):
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value)[:10], fmt)
        except ValueError:
            continue
    return None


def classify_fit_tier(total_score: float) -> str:
    """Map total score to tier A/B/C/D."""
    score = float(total_score)
    if score >= 75:
        return "A"
    if score >= 55:
        return "B"
    if score >= 35:
        return "C"
    return "D"


def recommend_action(tier: str, total_score: float) -> str:
    """Recommended action from fit tier."""
    if tier == "A":
        return "immediate_outreach"
    if tier == "B":
        return "apply_monitor"
    if tier == "C":
        return "learning_stretch"
    return "ignore"


def score_role_demand(
    job_row: dict | pd.Series,
    profile_keywords: list[str] | None = None,
    reference: datetime | None = None,
    sponsor_signal: str = "",
) -> dict:
    """
    Score a job row with 100-point Demand First formula:
    DFW 20, Recency 15, Profile 25, Early-career 15, Skills 10, Portfolio 10, Sponsor 5.
    """
    ref = reference or datetime.now()
    title = str(job_row.get("title", job_row.get("job_title", "")))
    description = str(job_row.get("description", ""))
    location = str(job_row.get("location", ""))
    role_family = str(job_row.get("role_family", ""))
    posted = str(job_row.get("posted_date", ""))
    job_url = str(job_row.get("job_url", job_row.get("source_url", "")))

    combined = f"{title} {description} {role_family}".lower()
    loc_lower = location.lower()

    dfw_score = 20 if any(t in loc_lower for t in DFW_TERMS) else 0

    posted_dt = _parse_date(posted)
    recency_score = 0
    if posted_dt and (ref - posted_dt).days <= 14:
        recency_score = 15
    elif posted_dt and (ref - posted_dt).days <= 30:
        recency_score = 8

    profile_hits = sum(1 for term in PROFILE_ROLE_FAMILIES if term in combined)
    profile_match_score = min(25, int(profile_hits / len(PROFILE_ROLE_FAMILIES) * 25) + (
        5 if any(k in combined for k in ("python", "sql", "cloud", "security", "data")) else 0
    ))
    profile_match_score = min(25, profile_match_score)

    early_hits = sum(1 for t in EARLY_CAREER_TERMS if t in combined)
    title_lower = title.lower()
    early_career_score = min(15, early_hits * 5) if early_hits else (
        15 if "analyst" in title_lower or "associate" in title_lower else 5
    )

    categories = categorize_keywords(f"{title} {description}")
    skill_cats = [k for k, v in categories.items() if v]
    skills_match_score = min(10, len(skill_cats) * 2)

    portfolio_terms = ("automation", "dashboard", "analytics", "security", "cloud", "python", "streamlit")
    portfolio_hits = sum(1 for t in portfolio_terms if t in combined)
    portfolio_support_score = min(10, portfolio_hits * 2 + 2)

    sponsor_lower = (sponsor_signal or str(job_row.get("visa_notes", ""))).lower()
    sponsor_score = 5 if any(s in sponsor_lower for s in ("sponsor", "h1b", "dol", "uscis")) else 2

    if profile_keywords:
        kw_lower = [k.lower() for k in profile_keywords]
        extra = sum(1 for k in kw_lower if k in combined)
        skills_match_score = min(10, skills_match_score + extra)

    total = (
        dfw_score
        + recency_score
        + profile_match_score
        + early_career_score
        + skills_match_score
        + portfolio_support_score
        + sponsor_score
    )
    total = min(100, total)
    tier = classify_fit_tier(total)
    action = recommend_action(tier, total)

    return {
        "job_id": job_row.get("job_id", ""),
        "company_id": job_row.get("company_id", ""),
        "company_name": job_row.get("company_name", job_row.get("company", "")),
        "job_title": title,
        "role_family": role_family,
        "posted_date": posted,
        "location": location,
        "dfw_score": dfw_score,
        "recency_score": recency_score,
        "profile_match_score": profile_match_score,
        "early_career_score": early_career_score,
        "skills_match_score": skills_match_score,
        "portfolio_support_score": portfolio_support_score,
        "sponsor_score": sponsor_score,
        "total_fit_score": total,
        "fit_tier": tier,
        "recommended_action": action,
        "source_url": job_url,
        "last_scored": ref.strftime("%Y-%m-%d"),
    }


def score_jobs_dataframe(
    jobs_df: pd.DataFrame,
    companies_df: pd.DataFrame | None = None,
    profile_keywords: list[str] | None = None,
    reference: datetime | None = None,
) -> list[dict]:
    """Score all jobs and return role demand score dicts."""
    sponsor_map = {}
    if companies_df is not None and not companies_df.empty:
        col = "company" if "company" in companies_df.columns else "company_name"
        sponsor_col = "sponsor_signal" if "sponsor_signal" in companies_df.columns else "notes"
        sponsor_map = dict(zip(companies_df[col], companies_df.get(sponsor_col, "")))

    results = []
    for _, row in jobs_df.iterrows():
        company = row.get("company_name", row.get("company", ""))
        score = score_role_demand(
            row,
            profile_keywords=profile_keywords,
            reference=reference,
            sponsor_signal=sponsor_map.get(company, ""),
        )
        results.append(score)
    return results


def save_role_demand_scores(scores: list[dict], path: Path | None = None) -> Path:
    """Persist role demand scores to CSV."""
    p = path or ROLE_DEMAND_SCORES_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROLE_DEMAND_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in scores:
            writer.writerow({col: row.get(col, "") for col in ROLE_DEMAND_COLUMNS})
    return p


def load_role_demand_scores(path: Path | None = None) -> pd.DataFrame:
    """Load role demand scores CSV."""
    p = path or ROLE_DEMAND_SCORES_PATH
    if not p.exists():
        return pd.DataFrame(columns=ROLE_DEMAND_COLUMNS)
    return pd.read_csv(p)
