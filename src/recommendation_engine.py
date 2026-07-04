"""Action recommendations: apply now, network first, research more, skip/watchlist."""

from src.role_fit_scorer import UNIVERSAL_PROFILE


def recommend(score: dict, company_priority: float = 50.0) -> dict:
    """Generate action recommendation from role fit and company priority."""
    fit = score.get("fit_score", 0)
    cats = score.get("category_scores", {})
    noise = cats.get("noise_risk", 0)
    sponsor = cats.get("sponsorship_signal", 50)
    network = cats.get("networking_opportunity", 50)

    composite = fit * 0.45 + company_priority * 0.25 + sponsor * 0.15 + network * 0.15 - noise * 0.2

    if noise >= 70:
        action = "skip/watchlist"
        rationale = "High noise risk — likely templated or stale posting."
    elif composite >= 75 and fit >= 65:
        action = "apply now"
        rationale = "Strong role fit and company priority — move quickly."
    elif network >= 60 and fit >= 50:
        action = "network first"
        rationale = "Good fit but warm intro will improve response rate."
    elif fit >= 40:
        action = "research more"
        rationale = "Moderate fit — validate sponsorship and team before applying."
    else:
        action = "skip/watchlist"
        rationale = "Low fit or priority — deprioritize unless market shifts."

    return {
        "action": action,
        "composite_score": round(composite, 1),
        "rationale": rationale,
        "profile": UNIVERSAL_PROFILE,
    }


def recommend_batch(scores: list[dict], company_scores: list[dict]) -> list[dict]:
    priority_map = {c["company"]: c["priority_score"] for c in company_scores}
    results = []
    for score in scores:
        company = score.get("company_name", "")
        rec = recommend(score, priority_map.get(company, 50))
        rec["job_id"] = score.get("job_id")
        rec["company_name"] = company
        rec["title"] = score.get("title")
        rec["fit_score"] = score.get("fit_score")
        results.append(rec)
    return results
