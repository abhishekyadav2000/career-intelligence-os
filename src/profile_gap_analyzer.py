"""Profile gap analysis against target role requirements."""

from src.keyword_extractor import SKILL_TAXONOMY, categorize_keywords
from src.role_fit_scorer import PROFILE_WEIGHTS, UNIVERSAL_PROFILE


def analyze_gaps(description: str, title: str = "") -> dict:
    """Identify skill gaps vs universal profile."""
    categories = categorize_keywords(f"{title} {description}")
    matched = [k for k in PROFILE_WEIGHTS if k in categories]
    gaps = [k for k in PROFILE_WEIGHTS if k not in categories]

    gap_details = []
    for gap in gaps:
        gap_details.append({
            "skill": gap,
            "suggested_proof": _proof_suggestion(gap),
            "priority": "High" if PROFILE_WEIGHTS[gap] >= 0.12 else "Medium",
        })

    coverage = round(len(matched) / len(PROFILE_WEIGHTS) * 100, 1)

    return {
        "profile": UNIVERSAL_PROFILE,
        "coverage_pct": coverage,
        "matched_skills": matched,
        "gaps": gap_details,
        "gap_count": len(gaps),
    }


def _proof_suggestion(skill: str) -> str:
    suggestions = {
        "python": "Build a Python ETL script with error handling and logging",
        "sql": "Write 5 analytics queries with window functions and CTEs",
        "cloud": "Deploy a secure VPC architecture diagram with IAM roles",
        "security": "Document an IAM least-privilege policy and SIEM use case",
        "data_analytics": "Create a KPI dashboard with data quality checks",
        "ai_automation": "Build a rule-based workflow automation with guardrails",
        "risk_grc": "Map NIST controls to a sample cloud application",
        "business_analysis": "Write user stories with acceptance criteria for a feature",
    }
    return suggestions.get(skill, "Add portfolio proof for this skill area")


def analyze_jobs_batch(jobs_df, scores: list[dict]) -> list[dict]:
    score_map = {s["job_id"]: s for s in scores}
    results = []
    for _, job in jobs_df.iterrows():
        gap = analyze_gaps(job.get("description", ""), job.get("title", ""))
        gap["job_id"] = job["job_id"]
        gap["company_name"] = job["company_name"]
        gap["title"] = job["title"]
        gap["fit_score"] = score_map.get(job["job_id"], {}).get("fit_score", 0)
        results.append(gap)
    return results
