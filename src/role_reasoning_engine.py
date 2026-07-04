"""Role reasoning engine — why roles exist and how to position proof-of-work."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_role_reasoning() -> pd.DataFrame:
    path = DATA_DIR / "role_reasoning.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def infer_role_reason(
    job_id: str,
    jobs_df: pd.DataFrame,
    reasoning_df: pd.DataFrame | None = None,
) -> dict:
    """Infer why a role exists using seeded reasoning and job metadata."""
    reasoning_df = reasoning_df if reasoning_df is not None else load_role_reasoning()
    job_rows = jobs_df[jobs_df["job_id"] == job_id]
    if job_rows.empty:
        return {"job_id": job_id, "found": False, "error": "Job not found"}

    job = job_rows.iloc[0]
    reason_rows = reasoning_df[reasoning_df["job_id"] == job_id]

    if not reason_rows.empty:
        r = reason_rows.iloc[0]
        questions = [q.strip() for q in str(r.get("priority_questions", "")).split(";") if q.strip()]
        help_bullets = [b.strip() for b in str(r.get("how_i_would_help", "")).split(";") if b.strip()]
        return {
            "job_id": job_id,
            "found": True,
            "title": job["title"],
            "company": job.get("company_name", job.get("company", "")),
            "why_role_exists": r["why_role_exists"],
            "business_problem": r["business_problem"],
            "likely_team": r["likely_team"],
            "success_metrics_30": r["success_metrics_30"],
            "success_metrics_60": r["success_metrics_60"],
            "success_metrics_90": r["success_metrics_90"],
            "how_i_would_help": help_bullets or [r["how_i_would_help"]],
            "priority_questions": questions,
            "role_family": job.get("role_family", ""),
            "source": "seeded_reasoning",
        }

    visa_notes = str(job.get("visa_notes", ""))
    business_problem = visa_notes.split("—")[0].strip() if "—" in visa_notes else visa_notes[:200]
    return {
        "job_id": job_id,
        "found": True,
        "title": job["title"],
        "company": job.get("company_name", job.get("company", "")),
        "why_role_exists": f"Role supports {business_problem.lower()} based on job description themes.",
        "business_problem": business_problem,
        "likely_team": job.get("role_cluster", job.get("role_family", "Technology")),
        "success_metrics_30": "Learn team tools and deliver first small contribution.",
        "success_metrics_60": "Own a workflow or analysis with documented outcomes.",
        "success_metrics_90": "Present measurable improvement to stakeholders.",
        "how_i_would_help": [
            "Apply Python/SQL and cloud security skills from portfolio projects.",
            "Demonstrate structured decision-making via Career Intelligence OS.",
        ],
        "priority_questions": [
            "What does success look like in the first 90 days?",
            "Which teams will I partner with most?",
            "What are the biggest current blockers?",
        ],
        "role_family": job.get("role_family", ""),
        "source": "inferred_from_jd",
    }


def map_role_to_business_problem(
    job_id: str,
    jobs_df: pd.DataFrame,
    reasoning_df: pd.DataFrame | None = None,
) -> str:
    """Return the primary business problem for a role."""
    reason = infer_role_reason(job_id, jobs_df, reasoning_df)
    return reason.get("business_problem", "Business problem not identified")


def map_role_to_proof_assets(
    job_id: str,
    proof_assets_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
) -> list[dict]:
    """Map proof assets to a role via tag matching."""
    from src.proof_asset_mapper import match_assets_to_role

    return match_assets_to_role(job_id, proof_assets_df, jobs_df)


def generate_role_questions(
    job_id: str,
    jobs_df: pd.DataFrame,
    reasoning_df: pd.DataFrame | None = None,
) -> list[str]:
    """Generate priority questions for a role conversation."""
    reason = infer_role_reason(job_id, jobs_df, reasoning_df)
    return reason.get("priority_questions", [])


def build_role_deep_dive(
    job_id: str,
    jobs_df: pd.DataFrame,
    reasoning_df: pd.DataFrame | None = None,
) -> dict:
    """Full role deep dive package for dashboard display."""
    reason = infer_role_reason(job_id, jobs_df, reasoning_df)
    job_rows = jobs_df[jobs_df["job_id"] == job_id]
    description = job_rows.iloc[0]["description"] if not job_rows.empty else ""

    keywords = []
    for kw in ["Python", "SQL", "IAM", "SIEM", "Kubernetes", "automation", "analytics", "cloud", "risk"]:
        if kw.lower() in description.lower():
            keywords.append(kw)

    return {
        **reason,
        "jd_keywords": keywords,
        "description_excerpt": description[:500] + ("..." if len(description) > 500 else ""),
        "plan_30_60_90": {
            "30_days": reason.get("success_metrics_30", ""),
            "60_days": reason.get("success_metrics_60", ""),
            "90_days": reason.get("success_metrics_90", ""),
        },
    }
