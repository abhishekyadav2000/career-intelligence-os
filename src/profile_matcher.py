"""Profile-to-job matching — score roles against the user's real background."""

from __future__ import annotations

import re
from typing import Any

from src.profile_manager import get_skills_for_matching, get_target_role_families, load_profile
from src.role_demand_scorer import classify_fit_tier

PLACEHOLDER_RE = re.compile(r"^\[.+\]$")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _skill_in_text(skill: str, text: str) -> bool:
    skill_norm = _normalize(skill)
    if not skill_norm or len(skill_norm) < 2:
        return False
    return skill_norm in text


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip()
        return bool(stripped) and not PLACEHOLDER_RE.match(stripped)
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def match_job_to_profile(job_row: dict | Any, profile: dict | None = None) -> dict:
    """
    Score how well a job matches the user's profile.

    Returns score (0-100), matched/missing skills, fit tier, and tier reason.
    """
    p = profile or load_profile()
    title = str(job_row.get("title", job_row.get("job_title", "")))
    description = str(job_row.get("description", ""))
    location = str(job_row.get("location", ""))
    role_family = str(job_row.get("role_family", ""))
    combined = _normalize(f"{title} {description} {role_family}")

    user_skills = get_skills_for_matching(p)
    matched_skills = [s for s in user_skills if _skill_in_text(s, combined)]
    missing_skills = [s for s in user_skills if s not in matched_skills][:8]

    skill_score = 0.0
    if user_skills:
        skill_score = min(50.0, (len(matched_skills) / len(user_skills)) * 50.0)

    target_roles = get_target_role_families(p)
    role_hits = sum(1 for r in target_roles if _normalize(r) in combined)
    role_score = min(25.0, role_hits * 8.0) if target_roles else 0.0

    target_locs = p.get("target_locations", [])
    loc_lower = location.lower()
    loc_score = 0.0
    if target_locs:
        if any(_normalize(loc) in loc_lower or loc_lower in _normalize(loc) for loc in target_locs):
            loc_score = 15.0
        elif "remote" in loc_lower and any("remote" in _normalize(l) for l in target_locs):
            loc_score = 12.0
    elif any(t in loc_lower for t in ("dallas", "plano", "irving", "dfw", "frisco")):
        loc_score = 10.0

    project_bonus = 0.0
    for proj in p.get("projects", []):
        if not isinstance(proj, dict):
            continue
        proj_text = _normalize(f"{proj.get('name', '')} {proj.get('description', '')}")
        proj_skills = proj.get("skills", [])
        if isinstance(proj_skills, str):
            proj_skills = [proj_skills]
        if any(_skill_in_text(s, combined) for s in proj_skills) or any(
            _skill_in_text(k, proj_text) for k in combined.split()[:20]
        ):
            project_bonus = min(10.0, project_bonus + 3.0)

    total = min(100.0, round(skill_score + role_score + loc_score + project_bonus, 1))
    tier = classify_fit_tier(total)
    tier_reason = _tier_reason(tier, matched_skills, missing_skills, role_hits, target_roles)

    return {
        "score": total,
        "fit_tier": tier,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "tier_reason": tier_reason,
        "skill_match_pct": round(len(matched_skills) / max(len(user_skills), 1) * 100, 1),
        "target_role_hits": role_hits,
    }


def _tier_reason(
    tier: str,
    matched: list[str],
    missing: list[str],
    role_hits: int,
    target_roles: list[str],
) -> str:
    if tier == "A":
        parts = [f"Strong overlap on {len(matched)} profile skills"]
        if role_hits:
            parts.append(f"matches {role_hits} target role famil{'y' if role_hits == 1 else 'ies'}")
        return "; ".join(parts) + "."
    if tier == "B":
        return (
            f"Good partial match ({len(matched)} skills aligned). "
            f"Gap areas: {', '.join(missing[:3]) or 'role family alignment'}."
        )
    if tier == "C":
        return (
            f"Stretch role — only {len(matched)} skills match. "
            f"Consider upskilling: {', '.join(missing[:4]) or 'core target skills'}."
        )
    if not matched and not target_roles:
        return "Profile incomplete — add skills and target roles for accurate matching."
    return f"Weak match — missing {', '.join(missing[:4]) or 'key skills'} for this role."


def explain_match(job: dict | Any, profile: dict | None = None) -> str:
    """Human-readable explanation of why a job is tier A/B/C/D for this profile."""
    p = profile or load_profile()
    result = match_job_to_profile(job, p)
    title = str(job.get("title", job.get("job_title", "this role")))
    tier = result["fit_tier"]
    score = result["score"]

    lines = [f"**{title}** — Profile match **{score}/100 (Tier {tier})**", "", result["tier_reason"]]

    if result["matched_skills"]:
        lines.append(f"\n**Skills you bring:** {', '.join(result['matched_skills'][:8])}")
    if result["missing_skills"]:
        lines.append(f"**Skills to emphasize or build:** {', '.join(result['missing_skills'][:6])}")

    target_roles = get_target_role_families(p)
    if target_roles and result["target_role_hits"]:
        lines.append(f"**Target role alignment:** {result['target_role_hits']} of your role families appear in this posting.")

    if tier == "A":
        lines.append("\n**Recommendation:** Prioritize — strong fit with your background.")
    elif tier == "B":
        lines.append("\n**Recommendation:** Apply and tailor proof assets to highlighted gaps.")
    elif tier == "C":
        lines.append("\n**Recommendation:** Learning stretch — network first or build missing proof.")
    else:
        lines.append("\n**Recommendation:** Low priority unless strategic for networking or industry entry.")

    return "\n".join(lines)
