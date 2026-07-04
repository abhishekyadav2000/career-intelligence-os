"""Company 360 profile engine — strategic intelligence from CSV datasets."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def load_company_profiles() -> pd.DataFrame:
    return _load_csv("company_profiles.csv")


def load_company_projects() -> pd.DataFrame:
    return _load_csv("company_projects.csv")


def load_research_sources() -> pd.DataFrame:
    return _load_csv("research_sources.csv")


def build_company_360(
    company_id: str,
    profiles_df: pd.DataFrame | None = None,
    projects_df: pd.DataFrame | None = None,
    sources_df: pd.DataFrame | None = None,
    people_df: pd.DataFrame | None = None,
) -> dict:
    """Assemble a 360-degree company view from structured CSV data."""
    profiles_df = profiles_df if profiles_df is not None else load_company_profiles()
    projects_df = projects_df if projects_df is not None else load_company_projects()
    sources_df = sources_df if sources_df is not None else load_research_sources()
    people_df = people_df if people_df is not None else _load_csv("people_map.csv")

    profile = profiles_df[profiles_df["company_id"] == company_id]
    if profile.empty:
        return {"company_id": company_id, "found": False, "error": "Company profile not found"}

    row = profile.iloc[0]
    company_projects = projects_df[projects_df["company_id"] == company_id]
    company_sources = sources_df[sources_df["company_id"] == company_id]
    company_people = people_df[people_df["company_id"] == company_id] if not people_df.empty else pd.DataFrame()

    themes = summarize_company_themes(company_projects, company_id)
    gaps = get_company_research_gaps(company_id, profiles_df, people_df, sources_df)

    return {
        "company_id": company_id,
        "found": True,
        "company_name": row["company_name"],
        "industry": row["industry"],
        "headquarters_region": row["headquarters_region"],
        "dfw_presence": row["dfw_presence"],
        "strategic_summary": row["strategic_summary"],
        "tech_stack_themes": [t.strip() for t in str(row["tech_stack_themes"]).split(";")],
        "growth_signals": row["growth_signals"],
        "risk_factors": row["risk_factors"],
        "sponsorship_context": row["sponsorship_context"],
        "priority_tier": row["priority_tier"],
        "last_updated": row["last_updated"],
        "projects": company_projects.to_dict("records"),
        "themes": themes,
        "sources": company_sources.to_dict("records"),
        "people_count": len(company_people),
        "verified_people": int(
            company_people[company_people["verification_status"] == "verified"].shape[0]
            if not company_people.empty and "verification_status" in company_people.columns
            else 0
        ),
        "research_gaps": gaps,
    }


def summarize_company_themes(projects_df: pd.DataFrame, company_id: str) -> list[dict]:
    """Summarize public project themes grouped by confidence level."""
    subset = projects_df[projects_df["company_id"] == company_id]
    if subset.empty:
        return []

    themes = []
    for theme, group in subset.groupby("theme"):
        confidences = group["confidence_level"].tolist()
        top_conf = "high" if "high" in confidences else ("medium" if "medium" in confidences else "low")
        themes.append({
            "theme": theme,
            "project_count": len(group),
            "confidence_level": top_conf,
            "descriptions": group["description"].tolist(),
        })
    themes.sort(key=lambda t: {"high": 3, "medium": 2, "low": 1}.get(t["confidence_level"], 0), reverse=True)
    return themes


def match_company_to_proof_assets(
    company_id: str,
    profiles_df: pd.DataFrame | None = None,
    proof_assets_df: pd.DataFrame | None = None,
) -> list[dict]:
    """Match proof assets to company themes via tag overlap."""
    from src.proof_asset_mapper import load_proof_assets, match_assets_to_company

    profiles_df = profiles_df if profiles_df is not None else load_company_profiles()
    proof_assets_df = proof_assets_df if proof_assets_df is not None else load_proof_assets()
    return match_assets_to_company(company_id, proof_assets_df, profiles_df)


def get_company_research_gaps(
    company_id: str,
    profiles_df: pd.DataFrame | None = None,
    people_df: pd.DataFrame | None = None,
    sources_df: pd.DataFrame | None = None,
) -> list[str]:
    """Identify research gaps based on placeholder people and unverified sources."""
    profiles_df = profiles_df if profiles_df is not None else load_company_profiles()
    people_df = people_df if people_df is not None else _load_csv("people_map.csv")
    sources_df = sources_df if sources_df is not None else load_research_sources()

    gaps = []
    profile = profiles_df[profiles_df["company_id"] == company_id]
    if profile.empty:
        gaps.append("Company profile missing — add to company_profiles.csv")
        return gaps

    company_people = people_df[people_df["company_id"] == company_id] if not people_df.empty else pd.DataFrame()
    if company_people.empty:
        gaps.append("No people mapped — run people-map research workflow")
    else:
        placeholders = company_people[company_people["verification_status"] == "placeholder"]
        if len(placeholders) == len(company_people):
            gaps.append("All contacts are TBD placeholders — verify hiring manager and recruiter before outreach")

    company_sources = sources_df[sources_df["company_id"] == company_id] if not sources_df.empty else pd.DataFrame()
    if company_sources.empty:
        gaps.append("No research sources logged — add public sources to research_sources.csv")
    elif "verified" in company_sources.columns:
        unverified = company_sources[company_sources["verified"] != "yes"]
        if not unverified.empty:
            gaps.append(f"{len(unverified)} source(s) need browser verification")

    if profile.iloc[0]["last_updated"] < "2026-06-01":
        gaps.append("Profile may be stale — refresh strategic summary")

    return gaps
