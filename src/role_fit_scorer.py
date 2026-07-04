"""Role fit scoring against universal enterprise technology profile."""

from src.keyword_extractor import SKILL_TAXONOMY, categorize_keywords

UNIVERSAL_PROFILE = (
    "Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics"
)

PROFILE_WEIGHTS: dict[str, float] = {
    "python": 0.15,
    "sql": 0.12,
    "cloud": 0.12,
    "security": 0.15,
    "data_analytics": 0.12,
    "ai_automation": 0.15,
    "risk_grc": 0.10,
    "business_analysis": 0.09,
}

SCORE_CATEGORIES = [
    "technical_fit",
    "business_fit",
    "sponsorship_signal",
    "dfw_relevance",
    "networking_opportunity",
    "noise_risk",
]


def _category_score(matched: list[str], category: str) -> float:
    if not matched:
        return 0.0
    max_phrases = len(SKILL_TAXONOMY.get(category, []))
    coverage = min(len(matched) / max(max_phrases * 0.3, 1), 1.0)
    return coverage * 100


def _technical_fit(categories: dict) -> float:
    tech_keys = ["python", "sql", "cloud", "security", "data_analytics", "ai_automation"]
    scores = [_category_score(categories.get(k, []), k) for k in tech_keys]
    return round(sum(scores) / len(scores), 1) if scores else 0.0


def _business_fit(categories: dict) -> float:
    biz_keys = ["business_analysis", "risk_grc"]
    scores = [_category_score(categories.get(k, []), k) for k in biz_keys]
    return round(sum(scores) / len(scores), 1) if scores else 0.0


def score_role_fit(
    description: str,
    title: str = "",
    location: str = "",
    visa_notes: str = "",
    sponsor_signal: str = "",
) -> dict:
    """Score job against universal profile with six decision categories."""
    combined = f"{title} {description}"
    categories = categorize_keywords(combined)

    dimension_scores: dict[str, float] = {}
    weighted_total = 0.0
    for skill, weight in PROFILE_WEIGHTS.items():
        matched = categories.get(skill, [])
        dim_score = _category_score(matched, skill)
        dimension_scores[skill] = round(dim_score, 1)
        weighted_total += dim_score * weight

    fit_score = round(weighted_total, 1)
    if fit_score >= 75:
        fit_label = "Strong Fit"
    elif fit_score >= 55:
        fit_label = "Good Fit"
    elif fit_score >= 35:
        fit_label = "Moderate Fit"
    else:
        fit_label = "Stretch Role"

    matched_categories = [k for k, v in categories.items() if v]
    gaps = [k for k in PROFILE_WEIGHTS if k not in matched_categories]

    from src.sponsorship_signal import score_sponsorship
    from src.noise_detector import detect_noise

    sponsorship = score_sponsorship(visa_notes, sponsor_signal)
    noise = detect_noise(description, title)
    dfw_score = 80.0 if any(x in (location or "").lower() for x in ("dallas", "plano", "irving", "fort worth", "dfw")) else 40.0

    category_scores = {
        "technical_fit": _technical_fit(categories),
        "business_fit": _business_fit(categories),
        "sponsorship_signal": sponsorship["score"],
        "dfw_relevance": dfw_score,
        "networking_opportunity": min(fit_score * 0.9, 100),
        "noise_risk": noise["risk_score"],
    }

    return {
        "fit_score": fit_score,
        "fit_label": fit_label,
        "profile": UNIVERSAL_PROFILE,
        "dimension_scores": dimension_scores,
        "category_scores": category_scores,
        "matched_categories": matched_categories,
        "gaps": gaps,
        "categories_found": categories,
        "sponsorship_detail": sponsorship,
        "noise_detail": noise,
    }


def score_jobs_dataframe(jobs_df, companies_df=None) -> list[dict]:
    """Score all jobs; optionally enrich with company sponsor signals."""
    sponsor_map = {}
    if companies_df is not None:
        sponsor_map = dict(zip(companies_df["company"], companies_df.get("sponsor_signal", "")))

    results = []
    for _, row in jobs_df.iterrows():
        score = score_role_fit(
            description=row.get("description", ""),
            title=row.get("title", ""),
            location=row.get("location", ""),
            visa_notes=row.get("visa_notes", ""),
            sponsor_signal=sponsor_map.get(row.get("company", row.get("company_name", "")), ""),
        )
        score["job_id"] = row.get("job_id")
        score["company_name"] = row.get("company_name", row.get("company"))
        score["title"] = row.get("title")
        results.append(score)
    return results
