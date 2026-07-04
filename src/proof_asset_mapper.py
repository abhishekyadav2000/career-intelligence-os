"""Proof asset mapping — connect portfolio artifacts to companies and roles."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

THEME_TAG_MAP = {
    "digital banking": ["enterprise", "data-analytics", "business-analysis"],
    "cloud migration": ["cloud-security", "enterprise", "python"],
    "ai automation": ["ai-automation", "governance", "python"],
    "cybersecurity": ["cloud-security", "cybersecurity", "iam", "siem"],
    "network modernization": ["enterprise", "cloud-security"],
    "connected vehicle data": ["data-analytics", "enterprise"],
}

ROLE_TAG_MAP = {
    "data analyst": ["data-analyst", "data-analytics", "streamlit", "python"],
    "cloud security": ["cloud-security", "cybersecurity", "iam", "siem"],
    "cybersecurity": ["cloud-security", "cybersecurity", "iam", "siem"],
    "ai automation": ["ai-automation", "governance", "python"],
    "technology analyst": ["enterprise", "python", "data-analytics"],
    "business systems": ["business-analysis", "enterprise"],
    "platform engineer": ["cloud-security", "python", "enterprise"],
    "operations technology": ["enterprise", "data-analytics", "python"],
}


def load_proof_assets() -> pd.DataFrame:
    path = DATA_DIR / "proof_assets.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _tag_overlap(asset_tags: str, target_tags: set[str]) -> float:
    tags = {t.strip().lower() for t in str(asset_tags).split(";") if t.strip()}
    if not tags or not target_tags:
        return 0.0
    overlap = len(tags & target_tags)
    return overlap / max(len(target_tags), 1)


def match_assets_to_role(
    job_id: str,
    proof_assets_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
) -> list[dict]:
    """Match proof assets to a job by title and description tag overlap."""
    job_rows = jobs_df[jobs_df["job_id"] == job_id]
    if job_rows.empty or proof_assets_df.empty:
        return []

    job = job_rows.iloc[0]
    title_lower = str(job["title"]).lower()
    target_tags: set[str] = set()
    for role_key, tags in ROLE_TAG_MAP.items():
        if role_key in title_lower:
            target_tags.update(tags)
    if not target_tags:
        target_tags = {"enterprise", "python", "data-analytics"}

    desc = str(job.get("description", "")).lower()
    if "security" in desc or "siem" in desc:
        target_tags.update({"cloud-security", "cybersecurity"})
    if "automation" in desc or "ai" in desc:
        target_tags.update({"ai-automation", "governance"})

    results = []
    for _, asset in proof_assets_df.iterrows():
        overlap = _tag_overlap(asset["tags"], target_tags)
        base_score = float(asset.get("relevance_score", 50))
        combined = round(base_score * 0.6 + overlap * 100 * 0.4, 1)
        results.append({
            "asset_id": asset["asset_id"],
            "asset_type": asset["asset_type"],
            "title": asset["title"],
            "description": asset["description"],
            "url_or_path": asset["url_or_path"],
            "match_score": combined,
            "tags": asset["tags"],
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def match_assets_to_company(
    company_id: str,
    proof_assets_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
) -> list[dict]:
    """Match proof assets to a company via theme tags and company packets."""
    if proof_assets_df.empty:
        return []

    profile = profiles_df[profiles_df["company_id"] == company_id]
    company_name = profile.iloc[0]["company_name"].lower() if not profile.empty else ""
    target_tags: set[str] = {"enterprise", "portfolio"}

    from src.company_profile_engine import load_company_projects

    projects = load_company_projects()
    company_projects = projects[projects["company_id"] == company_id]
    for _, proj in company_projects.iterrows():
        theme = str(proj["theme"]).lower()
        target_tags.update(THEME_TAG_MAP.get(theme, []))

    slug = company_name.replace(" ", "-").split("/")[0].strip()
    slug_token = slug.split()[0] if slug.split() else ""
    results = []
    for _, asset in proof_assets_df.iterrows():
        overlap = _tag_overlap(asset["tags"], target_tags)
        company_bonus = 15.0 if slug.replace(" ", "") in str(asset["tags"]).lower().replace("-", "") else 0.0
        packet_bonus = 20.0 if slug_token and slug_token in str(asset.get("url_or_path", "")).lower() else 0.0
        base_score = float(asset.get("relevance_score", 50))
        combined = round(base_score * 0.5 + overlap * 100 * 0.3 + company_bonus + packet_bonus * 0.2, 1)
        results.append({
            "asset_id": asset["asset_id"],
            "asset_type": asset["asset_type"],
            "title": asset["title"],
            "description": asset["description"],
            "url_or_path": asset["url_or_path"],
            "match_score": combined,
            "tags": asset["tags"],
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def identify_missing_proof(
    job_id: str,
    company_id: str,
    proof_assets_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
) -> list[str]:
    """Identify proof gaps for a company/role combination."""
    role_matches = match_assets_to_role(job_id, proof_assets_df, jobs_df)
    company_matches = match_assets_to_company(company_id, proof_assets_df, profiles_df)

    gaps = []
    top_role = role_matches[:3] if role_matches else []
    if not top_role or top_role[0]["match_score"] < 60:
        gaps.append("No strong role-specific proof asset — consider tailoring case study")

    asset_types = {a["asset_type"] for a in role_matches[:5]}
    if "case_study" not in asset_types:
        gaps.append("Missing case study match for this role family")
    if "dashboard" not in asset_types and "screenshot" not in asset_types:
        gaps.append("No live demo or screenshot ready for this role")

    company_name = ""
    profile = profiles_df[profiles_df["company_id"] == company_id]
    if not profile.empty:
        company_name = profile.iloc[0]["company_name"]
        slug = company_name.lower().split()[0]
        has_packet = any(slug in str(a.get("url_or_path", "")).lower() for a in company_matches[:5])
        if not has_packet:
            gaps.append(f"No company packet for {company_name} — create in company-packets/")

    return gaps


def get_top_proof_assets_for_display(
    job_id: str,
    company_id: str,
    proof_assets_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    n: int = 3,
) -> list[dict]:
    """Return top N proof assets blending role and company relevance."""
    role_matches = match_assets_to_role(job_id, proof_assets_df, jobs_df)
    company_matches = match_assets_to_company(company_id, proof_assets_df, profiles_df)

    merged: dict[str, dict] = {}
    for item in role_matches:
        merged[item["asset_id"]] = {**item, "match_score": item["match_score"] * 0.6}
    for item in company_matches:
        if item["asset_id"] in merged:
            merged[item["asset_id"]]["match_score"] += item["match_score"] * 0.4
        else:
            merged[item["asset_id"]] = {**item, "match_score": item["match_score"] * 0.4}

    ranked = sorted(merged.values(), key=lambda x: x["match_score"], reverse=True)
    return ranked[:n]
