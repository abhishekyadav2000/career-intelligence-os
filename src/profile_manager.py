"""User profile and portfolio management — in-app profile for simulator and dashboard."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from src.proof_asset_mapper import load_proof_assets, match_assets_to_company

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROFILE_PATH = DATA_DIR / "user_profile.yaml"
UPLOADS_DIR = DATA_DIR / "uploads"
RESUME_HIGHLIGHTS_PATH = UPLOADS_DIR / "resume_highlights.txt"

PLACEHOLDER_RE = re.compile(r"^\[.+\]$")

DEFAULT_PROFILE: dict[str, Any] = {
    "name": "[YOUR NAME]",
    "headline": "[YOUR HEADLINE — e.g. Enterprise Technology Analyst]",
    "positioning": "[YOUR 2-3 SENTENCE VALUE PROPOSITION]",
    "location": "DFW / [YOUR CITY]",
    "authorization": "[OPT/EAD, STEM OPT pathway, etc.]",
    "target_roles": [],
    "target_industries": [],
    "target_locations": ["Plano", "Dallas", "Irving", "Frisco", "Remote DFW"],
    "years_experience": None,
    "education": {
        "school": "[YOUR SCHOOL]",
        "degree": "[YOUR DEGREE]",
        "graduation": "[YYYY or expected]",
        "relevant_coursework": [],
    },
    "skills": {
        "technical": [],
        "tools": [],
        "domains": [],
    },
    "certifications": [],
    "experience_bullets": [],
    "projects": [],
    "portfolio_links": [],
    "proof_asset_ids": [],
    "star_stories": [],
    "career_goals": "",
    "deal_breakers": [],
    "salary_expectation_range": None,
    "preferred_company_tiers": [],
    "networking_positioning": "",
}

COMPLETENESS_FIELDS: dict[str, tuple[int, str]] = {
    "name": (5, "Name"),
    "headline": (5, "Headline"),
    "positioning": (8, "Positioning statement"),
    "location": (4, "Location"),
    "authorization": (5, "Work authorization"),
    "target_roles": (10, "Target role families"),
    "target_industries": (4, "Target industries"),
    "target_locations": (4, "Target locations"),
    "years_experience": (3, "Years of experience"),
    "education.school": (3, "Education — school"),
    "education.degree": (3, "Education — degree"),
    "skills.technical": (8, "Technical skills"),
    "skills.tools": (5, "Tools"),
    "skills.domains": (5, "Domain expertise"),
    "experience_bullets": (10, "Experience bullets"),
    "projects": (8, "Projects"),
    "star_stories": (8, "STAR stories"),
    "career_goals": (5, "Career goals"),
    "networking_positioning": (5, "Networking positioning"),
    "proof_asset_ids": (4, "Proof asset links"),
    "portfolio_links": (3, "Portfolio links"),
}

LIST_KEYS = (
    "target_roles",
    "target_industries",
    "target_locations",
    "certifications",
    "experience_bullets",
    "projects",
    "portfolio_links",
    "proof_asset_ids",
    "star_stories",
    "deal_breakers",
    "preferred_company_tiers",
)


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip()
        return bool(stripped) and not PLACEHOLDER_RE.match(stripped)
    if isinstance(value, (list, dict)):
        return len(value) > 0
    if isinstance(value, (int, float)):
        return value > 0
    return True


def _get_nested(profile: dict, dotted_key: str) -> Any:
    parts = dotted_key.split(".")
    cur: Any = profile
    for part in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if key in ("education", "skills") and isinstance(value, dict):
            sub = dict(merged.get(key, {}))
            sub.update(value)
            merged[key] = sub
        elif value is not None:
            merged[key] = value
    return merged


def _normalize_legacy_profile(profile: dict) -> dict:
    """Map legacy flat fields to expanded schema."""
    if "opt_status" in profile and not _is_filled(profile.get("authorization", "")):
        profile["authorization"] = profile.pop("opt_status")
    elif "opt_status" in profile:
        profile.pop("opt_status", None)

    if isinstance(profile.get("education"), str) and _is_filled(profile["education"]):
        profile["education"] = {
            "school": profile["education"],
            "degree": "",
            "graduation": "",
            "relevant_coursework": [],
        }

    skills = profile.get("skills")
    if isinstance(skills, list):
        profile["skills"] = {
            "technical": skills,
            "tools": [],
            "domains": [],
        }
    elif not isinstance(skills, dict):
        profile["skills"] = {"technical": [], "tools": [], "domains": []}

    return profile


def load_profile(path: Path | None = None) -> dict[str, Any]:
    """Load user profile from YAML; seed defaults if missing."""
    _ensure_dirs()
    profile_path = path or PROFILE_PATH
    if not profile_path.exists():
        save_profile(DEFAULT_PROFILE, profile_path)
        return dict(DEFAULT_PROFILE)

    with open(profile_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    merged = _deep_merge(DEFAULT_PROFILE, data)
    merged = _normalize_legacy_profile(merged)
    for key in LIST_KEYS:
        if merged.get(key) is None:
            merged[key] = []
    if merged.get("education") is None:
        merged["education"] = dict(DEFAULT_PROFILE["education"])
    if merged.get("skills") is None:
        merged["skills"] = dict(DEFAULT_PROFILE["skills"])
    return merged


def save_profile(profile: dict[str, Any], path: Path | None = None) -> Path:
    """Persist profile to YAML."""
    _ensure_dirs()
    profile_path = path or PROFILE_PATH
    with open(profile_path, "w", encoding="utf-8") as f:
        yaml.dump(profile, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return profile_path


def validate_profile(profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate profile structure and return errors/warnings."""
    p = profile or load_profile()
    errors: list[str] = []
    warnings: list[str] = []

    for key in ("name", "headline", "positioning"):
        if not _is_filled(p.get(key)):
            errors.append(f"Missing required field: {key}")

    skills = p.get("skills", {})
    if not isinstance(skills, dict):
        errors.append("skills must be an object with technical, tools, and domains lists")
    else:
        for sub in ("technical", "tools", "domains"):
            if sub not in skills:
                warnings.append(f"skills.{sub} not defined — will default to empty list")

    education = p.get("education", {})
    if isinstance(education, dict):
        if not _is_filled(education.get("school")) and not _is_filled(education.get("degree")):
            warnings.append("Education incomplete — add school and degree")
    elif isinstance(education, str) and not _is_filled(education):
        warnings.append("Education incomplete")

    for story in p.get("star_stories", []):
        if not isinstance(story, dict):
            errors.append("Each star_story must be an object")
            continue
        for field in ("situation", "task", "action", "result"):
            if not _is_filled(story.get(field)):
                warnings.append(f"STAR story '{story.get('title', story.get('id', '?'))}' missing {field}")

    for proj in p.get("projects", []):
        if isinstance(proj, dict) and not _is_filled(proj.get("name")):
            warnings.append("Project missing name")

    if not get_skills_for_matching(p):
        warnings.append("No skills defined — matching will be inaccurate")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def get_skills_for_matching(profile: dict[str, Any] | None = None) -> list[str]:
    """Flat deduplicated skill list for scoring engines."""
    p = profile or load_profile()
    p = _normalize_legacy_profile(dict(p))
    skills_obj = p.get("skills", {})
    flat: list[str] = []
    if isinstance(skills_obj, dict):
        for key in ("technical", "tools", "domains"):
            for item in skills_obj.get(key, []) or []:
                if _is_filled(str(item)):
                    flat.append(str(item).strip())
    elif isinstance(skills_obj, list):
        flat.extend(s.strip() for s in skills_obj if _is_filled(str(s)))

    for cert in p.get("certifications", []) or []:
        if _is_filled(str(cert)):
            flat.append(str(cert).strip())

    for proj in p.get("projects", []) or []:
        if isinstance(proj, dict):
            proj_skills = proj.get("skills", [])
            if isinstance(proj_skills, str):
                proj_skills = [proj_skills]
            for s in proj_skills or []:
                if _is_filled(str(s)):
                    flat.append(str(s).strip())

    seen: set[str] = set()
    deduped: list[str] = []
    for s in flat:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped


def get_target_role_families(profile: dict[str, Any] | None = None) -> list[str]:
    """Return normalized target role families for matching."""
    p = profile or load_profile()
    roles = p.get("target_roles", []) or []
    return [str(r).strip() for r in roles if _is_filled(str(r))]


def profile_completeness_score(profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return 0-100 completeness score and list of missing fields."""
    p = profile or load_profile()
    total_weight = sum(w for w, _ in COMPLETENESS_FIELDS.values())
    earned = 0.0
    missing: list[str] = []

    for field_key, (weight, label) in COMPLETENESS_FIELDS.items():
        value = _get_nested(p, field_key)
        if _is_filled(value):
            earned += weight
        else:
            missing.append(label)

    score = round(min(100.0, (earned / total_weight) * 100), 1)
    return {"score": score, "missing": missing, "earned_weight": earned, "total_weight": total_weight}


def build_positioning_statement(profile: dict[str, Any] | None = None) -> str:
    """Copy-ready positioning statement from profile data."""
    p = profile or load_profile()
    skills = get_skills_for_matching(p)[:6]
    skill_text = ", ".join(skills) if skills else "[your core skills]"
    roles = get_target_role_families(p)
    role_text = ", ".join(roles[:3]) if roles else "[target roles]"
    loc = p.get("location", "DFW")
    auth = p.get("authorization", p.get("opt_status", ""))
    goals = p.get("career_goals", "")
    net = p.get("networking_positioning", "")

    parts = [
        f"I'm {p.get('name', '[YOUR NAME]')}, {p.get('headline', '[YOUR HEADLINE]')}.",
        p.get("positioning", ""),
        f"Based in {loc}, targeting {role_text} roles.",
        f"Core strengths: {skill_text}.",
    ]
    if goals and _is_filled(goals):
        parts.append(f"Career goal: {goals}.")
    if net and _is_filled(net):
        parts.append(net)
    elif auth and _is_filled(auth):
        parts.append(auth)
    return " ".join(part for part in parts if part and _is_filled(part)).strip()


def get_profile_for_simulator(profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compact profile payload for interview simulator context."""
    p = profile or load_profile()
    education = p.get("education", {})
    edu_summary = education if isinstance(education, str) else (
        f"{education.get('degree', '')} — {education.get('school', '')}".strip(" —")
    )
    return {
        "name": p.get("name", ""),
        "headline": p.get("headline", ""),
        "positioning": p.get("positioning", ""),
        "networking_positioning": p.get("networking_positioning", ""),
        "skills": get_skills_for_matching(p),
        "experience_bullets": p.get("experience_bullets", [])[:8],
        "authorization": p.get("authorization", p.get("opt_status", "")),
        "star_stories": p.get("star_stories", []),
        "projects": p.get("projects", [])[:5],
        "proof_asset_ids": p.get("proof_asset_ids", []),
        "career_goals": p.get("career_goals", ""),
        "education": edu_summary,
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
    positioning = build_positioning_statement(p)
    completeness = profile_completeness_score(p)
    resume_highlights = ""
    if RESUME_HIGHLIGHTS_PATH.exists():
        resume_highlights = RESUME_HIGHLIGHTS_PATH.read_text(encoding="utf-8").strip()

    return {
        "profile": p,
        "proof_assets": assets,
        "company_matched_assets": company_assets[:5],
        "sixty_second_pitch": pitch,
        "positioning_statement": positioning,
        "completeness": completeness,
        "resume_highlights": resume_highlights,
    }


def build_sixty_second_pitch(profile: dict[str, Any] | None = None) -> str:
    """Generate a copy-ready 60-second pitch."""
    return build_positioning_statement(profile)


def profile_to_json(profile: dict[str, Any]) -> str:
    return json.dumps(profile, indent=2)
