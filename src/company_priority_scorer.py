"""Company priority scoring for enterprise targeting."""

import pandas as pd


def score_company(row: pd.Series, job_count: int = 0, contact_count: int = 0) -> dict:
    """Score a company for priority targeting."""
    notes = str(row.get("notes", "")).lower()
    sponsor = str(row.get("sponsor_signal", "")).lower()

    tier_score = 90 if "tier 1" in notes else 70 if "tier 2" in notes else 50
    sponsor_score = 80 if any(w in sponsor for w in ("h1b", "sponsor", "mega", "campus")) else 50
    pipeline_score = min(job_count * 10 + contact_count * 5, 100)

    priority = round(tier_score * 0.4 + sponsor_score * 0.35 + pipeline_score * 0.25, 1)

    if priority >= 80:
        label = "Attack First"
    elif priority >= 65:
        label = "High Priority"
    elif priority >= 50:
        label = "Monitor"
    else:
        label = "Watchlist"

    return {"priority_score": priority, "priority_label": label, "job_count": job_count, "contact_count": contact_count}


def score_companies(companies_df: pd.DataFrame, jobs_df: pd.DataFrame, contacts_df: pd.DataFrame) -> list[dict]:
    job_counts = jobs_df.groupby("company").size().to_dict()
    contact_counts = contacts_df.groupby("company").size().to_dict()

    results = []
    for _, row in companies_df.iterrows():
        company = row["company"]
        s = score_company(row, job_counts.get(company, 0), contact_counts.get(company, 0))
        s["company"] = company
        s["industry"] = row.get("industry", "")
        s["location"] = row.get("location", "")
        results.append(s)

    return sorted(results, key=lambda x: x["priority_score"], reverse=True)
