"""Rule-based conversation log analyzer for portfolio feedback loop."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "conversation_log_template.csv"
SAMPLE_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_conversation_log.csv"

RESPONSE_WARM = {"replied", "interested", "scheduled", "positive", "warm", "follow-up scheduled"}
RESPONSE_COLD = {"no reply", "declined", "not interested", "rejected", "ghosted", "closed"}


def load_conversation_log(path: Path | str | None = None) -> list[dict[str, str]]:
    """Load conversation log CSV; returns empty list if missing or header-only.

    Sample/demo rows live in sample_conversation_log.csv and are never loaded by default.
    """
    log_path = Path(path) if path else DEFAULT_LOG_PATH
    if not log_path.exists():
        return []

    resolved = log_path.resolve()
    if resolved == SAMPLE_LOG_PATH.resolve():
        return []

    with log_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [
            dict(row) for row in reader
            if any(v.strip() for v in row.values() if v)
            and not _is_sample_row(dict(row))
        ]

    return rows


def _is_sample_row(row: dict[str, str]) -> bool:
    """Detect legacy sample rows that may remain in user logs."""
    source = (row.get("source") or "").lower()
    if "sample" in source or "demo" in source:
        return True
    company = row.get("company", "")
    sample_companies = {
        "JPMorgan Chase", "Capital One", "Citi",
        "Toyota Motor North America", "AT&T",
    }
    sample_dates = {"2026-03-15", "2026-03-18", "2026-03-20", "2026-03-22", "2026-03-25"}
    if company in sample_companies and row.get("date", "") in sample_dates:
        return True
    return False


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _is_warm(response: str) -> bool:
    normalized = _normalize(response)
    return any(token in normalized for token in RESPONSE_WARM)


def _is_cold(response: str) -> bool:
    normalized = _normalize(response)
    return any(token in normalized for token in RESPONSE_COLD)


def analyze_conversations(rows: list[dict[str, str]]) -> dict:
    """Analyze conversation log and return structured feedback stats."""
    if not rows:
        return {
            "total_conversations": 0,
            "warm_companies": [],
            "cold_companies": [],
            "repeated_objections": [],
            "skill_gaps": [],
            "next_actions": [],
            "portfolio_improvements": [],
            "by_person_type": {},
            "by_company": {},
            "summary": "No conversation data yet — use the template CSV to log outreach and interviews.",
        }

    objections: Counter[str] = Counter()
    skill_gaps: Counter[str] = Counter()
    portfolio_gaps: Counter[str] = Counter()
    next_actions: list[dict[str, str]] = []
    warm_companies: set[str] = set()
    cold_companies: set[str] = set()
    by_person_type: Counter[str] = Counter()
    by_company: Counter[str] = Counter()

    for row in rows:
        company = row.get("company", "").strip()
        person_type = row.get("person_type", "").strip()
        response = row.get("response", "")
        insight = row.get("insight_gained", "")
        gap = row.get("portfolio_gap", "")
        action = row.get("next_action", "")
        follow_up = row.get("follow_up_date", "")

        if company:
            by_company[company] += 1
            if _is_warm(response):
                warm_companies.add(company)
            elif _is_cold(response):
                cold_companies.add(company)

        if person_type:
            by_person_type[person_type] += 1

        insight_lower = _normalize(insight)
        for phrase in ("sponsorship", "visa", "opt", "ead", "h-1b", "h1b"):
            if phrase in insight_lower:
                objections["Sponsorship / visa timing"] += 1
        for phrase in ("experience", "years", "senior", "junior"):
            if phrase in insight_lower:
                objections["Experience level mismatch"] += 1
        for phrase in ("clearance", "citizen", "us person"):
            if phrase in insight_lower:
                objections["Clearance / citizenship requirement"] += 1
        for phrase in ("culture fit", "team", "communication"):
            if phrase in insight_lower:
                objections["Soft skills / culture fit"] += 1

        if gap.strip():
            skill_gaps[gap.strip()] += 1
            portfolio_gaps[gap.strip()] += 1

        if action.strip():
            next_actions.append({
                "company": company,
                "action": action.strip(),
                "follow_up_date": follow_up.strip(),
                "person_type": person_type,
            })

    repeated_objections = [
        {"objection": k, "count": v}
        for k, v in objections.most_common(5)
        if v >= 1
    ]
    top_skill_gaps = [
        {"gap": k, "count": v}
        for k, v in skill_gaps.most_common(5)
    ]
    top_portfolio = [
        {"improvement": k, "count": v}
        for k, v in portfolio_gaps.most_common(5)
    ]

    warm_only = sorted(warm_companies - cold_companies)
    cold_only = sorted(cold_companies - warm_companies)

    summary_parts = [
        f"{len(rows)} conversations logged",
        f"{len(warm_only)} warm companies",
        f"{len(repeated_objections)} objection themes",
    ]
    if top_skill_gaps:
        summary_parts.append(f"top gap: {top_skill_gaps[0]['gap']}")

    return {
        "total_conversations": len(rows),
        "warm_companies": warm_only,
        "cold_companies": cold_only,
        "repeated_objections": repeated_objections,
        "skill_gaps": top_skill_gaps,
        "next_actions": next_actions[:10],
        "portfolio_improvements": top_portfolio,
        "by_person_type": dict(by_person_type),
        "by_company": dict(by_company),
        "summary": "; ".join(summary_parts),
    }


def get_dashboard_stats(path: Path | str | None = None) -> dict:
    """Convenience wrapper for dashboard consumption."""
    rows = load_conversation_log(path)
    return analyze_conversations(rows)
