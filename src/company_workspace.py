"""Company workspace helpers — focused single-company Mission Control view."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.company_profile_engine import build_company_360, load_company_profiles
from src.interview_simulator import load_interview_journey, load_interview_insights
from src.message_queue_engine import build_message_queue
from src.proof_asset_mapper import get_top_proof_assets_for_display, load_proof_assets
from src.profile_manager import get_portfolio_summary


def build_company_workspace(
    company_id: str,
    job_id: str,
    data: dict,
    mission_control: dict,
    *,
    reference: datetime | None = None,
) -> dict:
    """Build single-page company workspace payload scoped to one company."""
    ref = reference or datetime.now()
    companies_df = data.get("companies", pd.DataFrame())
    jobs_df = data.get("jobs", pd.DataFrame())
    profiles_df = data.get("company_profiles", load_company_profiles())
    projects_df = data.get("company_projects", pd.DataFrame())
    sources_df = data.get("research_sources", pd.DataFrame())
    people_df = data.get("people_map", pd.DataFrame())
    proof_df = data.get("proof_assets", load_proof_assets())

    company_row = companies_df[companies_df["company_id"] == company_id]
    company_name = company_row.iloc[0]["company_name"] if not company_row.empty else ""
    job_row = jobs_df[jobs_df["job_id"] == job_id] if job_id else pd.DataFrame()
    job_title = job_row.iloc[0]["title"] if not job_row.empty else ""
    role_family = job_row.iloc[0]["role_family"] if not job_row.empty else ""

    c360 = build_company_360(company_id, profiles_df, projects_df, sources_df, people_df)
    summary_lines = _intel_summary_lines(c360)

    action_queue = mission_control.get("action_queue", [])
    top_actions = action_queue[:3] if action_queue else []

    mq = build_message_queue(mission_control.get("cards", []), data)
    company_messages = [m for m in mq if m.get("company_name") == company_name]
    copy_message = company_messages[0].get("message_draft", "") if company_messages else ""

    proof_assets = get_top_proof_assets_for_display(
        job_id, company_id, proof_df, jobs_df, profiles_df, n=3,
    )
    portfolio = get_portfolio_summary(company_id)

    insights = load_interview_insights(company_id, role_family)
    journey = load_interview_journey(company_id, job_id)

    last_updated = c360.get("last_updated", ref.strftime("%Y-%m-%d"))
    source_urls = c360.get("sources", [])
    has_verified_source = bool(source_urls) or bool(c360.get("projects"))

    return {
        "company_id": company_id,
        "company_name": company_name,
        "job_id": job_id,
        "job_title": job_title,
        "role_family": role_family,
        "intel_summary_lines": summary_lines,
        "top_actions": top_actions,
        "copy_message": copy_message,
        "proof_assets": proof_assets,
        "portfolio_pitch": portfolio.get("sixty_second_pitch", ""),
        "interview_journey": journey,
        "verified_insights_count": len(insights),
        "last_updated": last_updated,
        "has_verified_source": has_verified_source,
        "company_360": c360,
    }


def _intel_summary_lines(c360: dict) -> list[str]:
    if not c360.get("found"):
        return ["Company profile not found — enrich company_profiles.csv."]
    lines = []
    summary = c360.get("strategic_summary", "")
    if summary:
        lines.append(summary[:180] + ("…" if len(summary) > 180 else ""))
    themes = c360.get("themes", [])
    if themes:
        theme_text = ", ".join(t.get("theme", str(t)) for t in themes[:3])
        lines.append(f"Active themes: {theme_text}")
    tier = c360.get("priority_tier", "")
    dfw = c360.get("dfw_presence", "")
    if tier or dfw:
        lines.append(f"{tier} · DFW: {dfw}" if dfw else tier)
    while len(lines) < 3:
        lines.append("Verify latest intel via research_sources before outreach.")
    return lines[:3]
