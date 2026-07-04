"""Role fit scoring against universal profile."""

from src.keywords import SKILL_TAXONOMY, categorize_keywords

UNIVERSAL_PROFILE = (
    "Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics"
)

# Weighted skill dimensions from DFW workbook capability matrix
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

PROFILE_SKILLS = list(PROFILE_WEIGHTS.keys())


def _category_score(matched: list[str], category: str) -> float:
    """Score a single category based on keyword matches."""
    if not matched:
        return 0.0
    max_phrases = len(SKILL_TAXONOMY.get(category, []))
    coverage = min(len(matched) / max(max_phrases * 0.3, 1), 1.0)
    return coverage * 100


def score_role_fit(description: str, title: str = "") -> dict:
    """
    Score how well a job matches the universal profile.

    Returns score 0-100 with per-dimension breakdown.
    """
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
    gaps = [k for k in PROFILE_SKILLS if k not in matched_categories]

    return {
        "fit_score": fit_score,
        "fit_label": fit_label,
        "profile": UNIVERSAL_PROFILE,
        "dimension_scores": dimension_scores,
        "matched_categories": matched_categories,
        "gaps": gaps,
        "categories_found": categories,
    }


def score_jobs_dataframe(jobs_df) -> list[dict]:
    """Score all jobs in a DataFrame."""
    results = []
    for _, row in jobs_df.iterrows():
        score = score_role_fit(
            description=row.get("description", ""),
            title=row.get("title", ""),
        )
        score["job_id"] = row.get("job_id")
        score["company_name"] = row.get("company_name")
        score["title"] = row.get("title")
        results.append(score)
    return results
