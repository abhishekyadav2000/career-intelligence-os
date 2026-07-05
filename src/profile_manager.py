"""User profile and portfolio management — in-app profile for simulator and dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.proof_asset_mapper import load_proof_assets, match_assets_to_company

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROFILE_PATH = DATA_DIR / "user_profile.yaml"
UPLOADS_DIR = DATA_DIR / "uploads"
RESUME_HIGHLIGHTS_PATH = UPLOADS_DIR / "resume_highlights.txt"

DEFAULT_PROFILE: dict[str, Any] = {
    "name": "Abhishek",
    "headline": "Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics",
    "positioning": (
        "Enterprise technology analyst focused on AI automation, cloud security evidence, "
        "and data-driven decision systems for regulated industries."
    ),
    "skills": [
        "Python",
        "SQL",
        "Streamlit",
        "Cloud Security (IAM/SIEM)",
        "AI Automation & Governance",
        "Data Analytics",
        "Enterprise Architecture",
    ],
    "experience_bullets": [
        "Built Career Intelligence OS — sponsor-aware role-fit scoring and interview prep dashboard (Streamlit + Python).",
        "Developed AI agent risk scoring framework with guardrails and responsible automation controls.",
        "Delivered secure cloud evidence lab covering IAM policy review and SIEM alert tuning.",
        "Designed data pipelines and KPI dashboards for enterprise decision support.",
    ],
    "education": "MS/MBA-track STEM graduate — enterprise technology and analytics focus",
    "opt_status": "OPT/EAD authorized; STEM OPT pathway eligible",
    "portfolio_links": [
        {"title": "Career Intelligence OS Demo", "url": "dashboard/app.py"},
        {"title": "AI Agent Risk Scoring Case Study", "url": "case-studies/ai-agent-risk-scoring.md"},
        {"title": "Secure Cloud Evidence Lab", "url": "case-studies/secure-cloud-evidence-lab.md"},
    ],
    "proof_asset_ids": ["PA001", "PA002", "PA003", "PA004", "PA013"],
    "star_stories": [
        {
            "id": "STAR001",
            "title": "Career Intelligence OS",
            "situation": "Fragmented DFW enterprise hiring data across 50+ employers.",
            "task": "Build a unified decision system for role fit, sponsorship signals, and interview prep.",
            "action": "Designed CSV schema, scoring engine, and Streamlit dashboard with verified sources.",
            "result": "Working demo with Mission Control, ICC briefs, and proof-matched outreach.",
            "tags": ["python", "streamlit", "data-analytics", "enterprise"],
        },
        {
            "id": "STAR002",
            "title": "AI Agent Risk Scoring",
            "situation": "Teams deploying AI agents without consistent risk controls.",
            "task": "Create a governance framework for agent automation.",
            "action": "Built risk scoring model with guardrails, audit trails, and escalation paths.",
            "result": "Documented case study demonstrating responsible AI automation patterns.",
            "tags": ["ai-automation", "governance", "risk-controls"],
        },
        {
            "id": "STAR003",
            "title": "Secure Cloud Evidence Lab",
            "situation": "Cloud security audits required IAM and SIEM evidence collection.",
            "task": "Demonstrate hands-on cloud security analysis skills.",
            "action": "Reviewed IAM policies, tuned SIEM alerts, and documented findings.",
            "result": "Portfolio-ready evidence lab with synthetic artifacts and remediation notes.",
            "tags": ["cloud-security", "iam", "siem"],
        },
    ],
}


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def load_profile(path: Path | None = None) -> dict[str, Any]:
    """Load user profile from YAML; seed defaults if missing."""
    _ensure_dirs()
    profile_path = path or PROFILE_PATH
    if not profile_path.exists():
        save_profile(DEFAULT_PROFILE, profile_path)
        return dict(DEFAULT_PROFILE)

    with open(profile_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    merged = {**DEFAULT_PROFILE, **data}
    for key in ("skills", "experience_bullets", "portfolio_links", "proof_asset_ids", "star_stories"):
        if key not in merged or merged[key] is None:
            merged[key] = DEFAULT_PROFILE.get(key, [])
    return merged


def save_profile(profile: dict[str, Any], path: Path | None = None) -> Path:
    """Persist profile to YAML."""
    _ensure_dirs()
    profile_path = path or PROFILE_PATH
    with open(profile_path, "w", encoding="utf-8") as f:
        yaml.dump(profile, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return profile_path


def get_profile_for_simulator(profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compact profile payload for interview simulator context."""
    p = profile or load_profile()
    return {
        "name": p.get("name", ""),
        "headline": p.get("headline", ""),
        "positioning": p.get("positioning", ""),
        "skills": p.get("skills", []),
        "experience_bullets": p.get("experience_bullets", [])[:5],
        "opt_status": p.get("opt_status", ""),
        "star_stories": p.get("star_stories", []),
        "proof_asset_ids": p.get("proof_asset_ids", []),
    }


def get_portfolio_summary(
    company_id: str | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pull proof assets + profile for dashboard display."""
    p = profile or load_profile()
    proof_df = load_proof_assets()
    asset_ids = p.get("proof_asset_ids", [])
    assets = []
    if not proof_df.empty and asset_ids:
        matched = proof_df[proof_df["asset_id"].isin(asset_ids)]
        assets = matched.to_dict("records")

    company_assets = []
    if company_id:
        from src.company_profile_engine import load_company_profiles

        profiles_df = load_company_profiles()
        company_assets = match_assets_to_company(company_id, proof_df, profiles_df)

    pitch = build_sixty_second_pitch(p)
    resume_highlights = ""
    if RESUME_HIGHLIGHTS_PATH.exists():
        resume_highlights = RESUME_HIGHLIGHTS_PATH.read_text(encoding="utf-8").strip()

    return {
        "profile": p,
        "proof_assets": assets,
        "company_matched_assets": company_assets[:5],
        "sixty_second_pitch": pitch,
        "resume_highlights": resume_highlights,
    }


def build_sixty_second_pitch(profile: dict[str, Any] | None = None) -> str:
    """Generate a copy-ready 60-second pitch."""
    p = profile or load_profile()
    skills = ", ".join(p.get("skills", [])[:6])
    bullets = p.get("experience_bullets", [])[:2]
    bullet_text = " ".join(bullets)
    opt = p.get("opt_status", "")
    return (
        f"Hi, I'm {p.get('name', '')}. {p.get('headline', '')}. "
        f"{p.get('positioning', '')} "
        f"Key strengths: {skills}. "
        f"{bullet_text} "
        f"{opt}"
    ).strip()


def profile_to_json(profile: dict[str, Any]) -> str:
    return json.dumps(profile, indent=2)
