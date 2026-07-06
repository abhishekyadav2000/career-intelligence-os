"""Demand intelligence engine — signals before people (v1.3)."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from src.role_demand_scorer import classify_fit_tier, load_role_demand_scores, score_role_demand

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEMAND_SIGNALS_PATH = DATA_DIR / "company_demand_signals.csv"


def load_demand_signals(company_id: str | None = None, path: Path | None = None) -> pd.DataFrame:
    """Load demand signals, optionally filtered by company_id."""
    p = path or DEMAND_SIGNALS_PATH
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    if company_id and "company_id" in df.columns:
        return df[df["company_id"] == company_id].copy()
    return df


def get_recent_hiring_signals(
    company_id: str,
    days: int = 14,
    reference: datetime | None = None,
) -> list[dict]:
    """Return demand signals within the last N days for a company."""
    ref = reference or datetime.now()
    cutoff = ref - timedelta(days=days)
    df = load_demand_signals(company_id)
    if df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        sig_date = row.get("signal_date", "")
        try:
            dt = datetime.strptime(str(sig_date)[:10], "%Y-%m-%d")
        except ValueError:
            continue
        if dt.date() >= cutoff.date():
            results.append(row.to_dict())
    results.sort(key=lambda r: r.get("relevance_score", 0), reverse=True)
    return results


def get_company_demand_summary(company_id: str, reference: datetime | None = None) -> dict:
    """Aggregate demand picture for one company."""
    ref = reference or datetime.now()
    signals = load_demand_signals(company_id)
    recent = get_recent_hiring_signals(company_id, days=14, reference=ref)
    demand_scores = load_role_demand_scores()
    company_jobs = pd.DataFrame()
    if not demand_scores.empty and "company_id" in demand_scores.columns:
        company_jobs = demand_scores[demand_scores["company_id"] == company_id]

    tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for _, row in company_jobs.iterrows():
        tier = str(row.get("fit_tier", "D"))
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    signal_types: dict[str, int] = {}
    tech_areas: set[str] = set()
    for _, row in signals.iterrows():
        stype = str(row.get("signal_type", ""))
        signal_types[stype] = signal_types.get(stype, 0) + 1
        area = str(row.get("technology_area", ""))
        if area and area != "nan":
            tech_areas.add(area)

    job_postings = signals[signals["signal_type"] == "job_posting"] if not signals.empty else pd.DataFrame()

    return {
        "company_id": company_id,
        "total_signals": len(signals),
        "recent_signals_14d": len(recent),
        "job_posting_signals": len(job_postings),
        "signal_types": signal_types,
        "technology_areas": sorted(tech_areas),
        "tier_a_roles": tier_counts.get("A", 0),
        "tier_b_roles": tier_counts.get("B", 0),
        "tier_c_roles": tier_counts.get("C", 0),
        "tier_d_roles": tier_counts.get("D", 0),
        "has_recent_demand": len(recent) > 0,
        "has_tier_a": tier_counts.get("A", 0) > 0,
        "top_roles": company_jobs.sort_values("total_fit_score", ascending=False).head(5).to_dict("records")
        if not company_jobs.empty
        else [],
    }


def score_role_demand_export(job_row: dict, profile_keywords: list[str] | None = None) -> dict:
    """Public wrapper re-exporting scorer for engine consumers."""
    return score_role_demand(job_row, profile_keywords=profile_keywords)


def classify_fit_tier_export(total_score: float) -> str:
    return classify_fit_tier(total_score)
