"""ICC global selector state — shared across all dashboard tabs."""

from __future__ import annotations

import pandas as pd

CONVERSATION_TYPES = ["recruiter", "hiring manager", "peer", "alumni", "informational"]
INTERVIEW_STAGES = [
    "initial outreach",
    "recruiter screen",
    "hiring manager screen",
    "technical interview",
    "final round",
    "follow-up",
]


def build_company_options(
    companies_df: pd.DataFrame,
    company_rank_df: pd.DataFrame | None = None,
    search: str = "",
) -> list[str]:
    """Return company_id list sorted by priority then name, optionally filtered."""
    df = companies_df.copy()
    if company_rank_df is not None and not company_rank_df.empty:
        rank_map = dict(zip(company_rank_df["company"], company_rank_df["priority_score"]))
        df["priority_score"] = df["company_name"].map(rank_map).fillna(0)
    else:
        df["priority_score"] = df.get("rank", 999)

    if search.strip():
        query = search.strip().lower()
        df = df[df["company_name"].str.lower().str.contains(query, na=False)]

    df = df.sort_values(["priority_score", "company_name"], ascending=[False, True])
    return df["company_id"].tolist()


def format_company_option(company_id: str, companies_df: pd.DataFrame) -> str:
    row = companies_df[companies_df["company_id"] == company_id]
    if row.empty:
        return company_id
    record = row.iloc[0]
    tier = record.get("priority_tier", "Tier 2")
    return f"{record['company_name']} ({tier})"


def get_jobs_for_company(company_id: str, jobs_df: pd.DataFrame) -> pd.DataFrame:
    return jobs_df[jobs_df["company_id"] == company_id].sort_values("title")


def format_job_option(job_id: str, jobs_df: pd.DataFrame) -> str:
    row = jobs_df[jobs_df["job_id"] == job_id]
    if row.empty:
        return job_id
    record = row.iloc[0]
    return f"{record['title']} ({job_id})"


def _sync_job_for_company(session_state, companies_df: pd.DataFrame, jobs_df: pd.DataFrame) -> None:
    company_id = session_state.icc_company_id
    company_jobs = get_jobs_for_company(company_id, jobs_df)
    if company_jobs.empty:
        session_state.icc_job_id = ""
        session_state.icc_job_title = ""
        return

    job_ids = company_jobs["job_id"].tolist()
    if session_state.get("icc_job_id") not in job_ids:
        session_state.icc_job_id = job_ids[0]

    job_row = jobs_df[jobs_df["job_id"] == session_state.icc_job_id]
    if not job_row.empty:
        session_state.icc_job_title = job_row.iloc[0]["title"]

    company_row = companies_df[companies_df["company_id"] == company_id]
    if not company_row.empty:
        session_state.icc_company_name = company_row.iloc[0]["company_name"]


def init_icc_state(session_state, companies_df: pd.DataFrame, jobs_df: pd.DataFrame) -> None:
    """Initialize ICC session keys once; migrate legacy widget keys."""
    if "icc_company_id" not in session_state:
        first = companies_df.iloc[0]
        session_state.icc_company_id = first["company_id"]
        session_state.icc_company_name = first["company_name"]

    if "icc_person_type" not in session_state:
        session_state.icc_person_type = "hiring manager"
    if "icc_interview_stage" not in session_state:
        session_state.icc_interview_stage = "hiring manager screen"
    if "icc_company_search" not in session_state:
        session_state.icc_company_search = ""
    if "current_brief" not in session_state:
        session_state.current_brief = None
    if "brief_markdown" not in session_state:
        session_state.brief_markdown = ""

    # Migrate legacy Streamlit keys from earlier dashboard versions
    if "icc_company" in session_state:
        legacy_name = session_state.pop("icc_company")
        match = companies_df[companies_df["company_name"] == legacy_name]
        if not match.empty:
            session_state.icc_company_id = match.iloc[0]["company_id"]
            session_state.icc_company_name = legacy_name
    if "icc_conv_type" in session_state:
        session_state.icc_person_type = session_state.pop("icc_conv_type")
    if "icc_stage" in session_state:
        session_state.icc_interview_stage = session_state.pop("icc_stage")
    if "icc_job" in session_state and not session_state.get("icc_job_id"):
        session_state.icc_job_id = session_state.pop("icc_job")

    _sync_job_for_company(session_state, companies_df, jobs_df)


def on_company_change(session_state, companies_df: pd.DataFrame, jobs_df: pd.DataFrame) -> None:
    company_id = session_state.icc_company_id
    row = companies_df[companies_df["company_id"] == company_id]
    if not row.empty:
        session_state.icc_company_name = row.iloc[0]["company_name"]
    session_state.current_brief = None
    session_state.brief_markdown = ""
    _sync_job_for_company(session_state, companies_df, jobs_df)


def on_job_change(session_state, jobs_df: pd.DataFrame) -> None:
    job_id = session_state.icc_job_id
    row = jobs_df[jobs_df["job_id"] == job_id]
    if not row.empty:
        session_state.icc_job_title = row.iloc[0]["title"]
        session_state.icc_company_id = row.iloc[0]["company_id"]
    session_state.current_brief = None
    session_state.brief_markdown = ""


def set_target(
    session_state,
    company_id: str,
    job_id: str,
    companies_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
) -> None:
    """Set global target from Mission Control or ranking actions."""
    session_state.icc_company_id = company_id
    session_state.icc_job_id = job_id
    on_company_change(session_state, companies_df, jobs_df)
    on_job_change(session_state, jobs_df)


def resolve_icc_context(session_state, companies_df: pd.DataFrame, jobs_df: pd.DataFrame) -> dict:
    init_icc_state(session_state, companies_df, jobs_df)
    company_id = session_state.icc_company_id
    job_id = session_state.icc_job_id
    company_row = companies_df[companies_df["company_id"] == company_id]
    job_row = jobs_df[jobs_df["job_id"] == job_id] if job_id else pd.DataFrame()
    return {
        "company_id": company_id,
        "company_name": session_state.icc_company_name,
        "job_id": job_id,
        "job_title": session_state.icc_job_title,
        "person_type": session_state.icc_person_type,
        "interview_stage": session_state.icc_interview_stage,
        "company_row": company_row.iloc[0] if not company_row.empty else None,
        "job_row": job_row.iloc[0] if not job_row.empty else None,
        "selection_complete": bool(company_id and job_id),
    }
