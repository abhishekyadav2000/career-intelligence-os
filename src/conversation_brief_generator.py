"""Conversation brief generator — end-to-end interview prep packages."""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd

from src.company_profile_engine import build_company_360, load_company_profiles
from src.people_power_mapper import rank_contacts_for_conversation, load_people_map
from src.proof_asset_mapper import get_top_proof_assets_for_display, identify_missing_proof, load_proof_assets
from src.role_reasoning_engine import build_role_deep_dive, infer_role_reason, load_role_reasoning

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BRIEFS_PATH = DATA_DIR / "conversation_briefs.csv"


def generate_conversation_script(
    company_name: str,
    job_title: str,
    conversation_type: str,
    interview_stage: str,
    role_reason: dict,
    top_proof: list[dict],
) -> str:
    """Generate a conversation opening script."""
    proof_ref = top_proof[0]["title"] if top_proof else "my portfolio projects"
    business_problem = role_reason.get("business_problem", "your team's priorities")

    scripts = {
        "recruiter": (
            f"Hi — I'm exploring the {job_title} opportunity at {company_name}. "
            f"My background aligns with {business_problem.lower()}. "
            f"I'd like to share how {proof_ref} demonstrates the Python, SQL, and analytics skills this role requires. "
            f"Could we schedule a brief call to discuss the process and timeline?"
        ),
        "hiring manager": (
            f"Thank you for the time. I'm excited about the {job_title} role at {company_name} because it addresses "
            f"{business_problem.lower()}. In my portfolio, {proof_ref} shows how I approach structured "
            f"decision-making with measurable outcomes. I'd love to learn what success looks like in the first 90 days "
            f"and where I could contribute immediately."
        ),
        "peer": (
            f"Hi — I'm researching the {job_title} path at {company_name} and would appreciate "
            f"a brief informational chat about your team's day-to-day. No referral ask — I'm focused on "
            f"understanding the role landscape and tooling first."
        ),
        "alumni": (
            f"Hi — I noticed we share a university connection. I'm exploring technology roles at {company_name} "
            f"and would value a brief chat about your experience on the team."
        ),
    }
    base = scripts.get(conversation_type.lower(), scripts["recruiter"])
    if interview_stage == "follow-up":
        base = f"Following up on our {conversation_type} conversation about {job_title} at {company_name}. " + base
    return base


def generate_opt_disclosure(include: bool = True) -> str:
    """Generate optional sponsorship disclosure text."""
    if not include:
        return "[Optional — not included] Work authorization disclosure omitted per user preference."
    return (
        "I'm currently authorized to work in the U.S. on OPT/EAD and targeting roles aligned with my STEM OPT "
        "pathway. I'm being transparent early about future sponsorship compatibility where relevant, and I'm "
        "happy to follow the company's process for roles that support that pathway."
    )


def generate_follow_up(
    company_name: str,
    job_title: str,
    conversation_type: str,
    insight_gained: str = "",
) -> str:
    """Generate a follow-up message template."""
    insight_line = f" I appreciated learning that {insight_gained}." if insight_gained else ""
    return (
        f"Hi — thank you again for our conversation about the {job_title} role at {company_name}.{insight_line} "
        f"As discussed, I'm sharing my portfolio link and the Career Intelligence OS walkthrough. "
        f"Please let me know if there's anything else I can provide for the next step."
    )


def generate_next_action(
    conversation_type: str,
    interview_stage: str,
    research_gaps: list[str],
    missing_proof: list[str],
) -> list[str]:
    """Generate prioritized next actions."""
    actions = []
    if research_gaps:
        actions.append(f"Research gap: {research_gaps[0]}")
    if missing_proof:
        actions.append(f"Proof gap: {missing_proof[0]}")
    if interview_stage == "initial outreach":
        actions.append("Send outreach message via careers portal or verified contact")
        actions.append("Log conversation in conversation_log_template.csv")
    elif interview_stage == "recruiter screen":
        actions.append("Prepare 2-minute elevator pitch with proof asset reference")
        actions.append("Review sponsorship disclosure script")
    elif interview_stage == "hiring manager screen":
        actions.append("Demo Career Intelligence OS dashboard live or via walkthrough")
        actions.append("Prepare 30/60/90 day plan talking points")
    elif interview_stage == "technical interview":
        actions.append("Review role-specific interview packet")
        actions.append("Practice technical topics from interview prep tab")
    else:
        actions.append("Send thank-you follow-up within 24 hours")
        actions.append("Update conversation brief with insights gained")
    if conversation_type == "hiring manager":
        actions.insert(0, "Lead with business problem alignment and proof-of-work demo")
    return actions[:5]


def generate_conversation_brief(
    company_id: str,
    job_id: str,
    jobs_df: pd.DataFrame,
    conversation_type: str = "hiring manager",
    interview_stage: str = "hiring manager screen",
    include_disclosure: bool = True,
) -> dict:
    """Generate a full conversation brief with all seven sections."""
    profiles_df = load_company_profiles()
    people_df = load_people_map()
    proof_df = load_proof_assets()
    reasoning_df = load_role_reasoning()

    company_360 = build_company_360(company_id, profiles_df, people_df=people_df)
    role_intel = build_role_deep_dive(job_id, jobs_df, reasoning_df)
    people_ranked = rank_contacts_for_conversation(company_id, conversation_type, interview_stage, people_df)
    top_proof = get_top_proof_assets_for_display(job_id, company_id, proof_df, jobs_df, profiles_df, n=5)
    missing = identify_missing_proof(job_id, company_id, proof_df, jobs_df, profiles_df)

    job_rows = jobs_df[jobs_df["job_id"] == job_id]
    job_title = job_rows.iloc[0]["title"] if not job_rows.empty else "Unknown Role"
    company_name = company_360.get("company_name", "Unknown Company")

    from src.interview_topic_mapper import generate_interview_topics_for_job

    interview_prep = generate_interview_topics_for_job(job_id, jobs_df)

    script = generate_conversation_script(
        company_name, job_title, conversation_type, interview_stage, role_intel, top_proof
    )
    disclosure = generate_opt_disclosure(include_disclosure)
    follow_up = generate_follow_up(company_name, job_title, conversation_type)
    next_actions = generate_next_action(
        conversation_type, interview_stage,
        company_360.get("research_gaps", []), missing,
    )

    brief = {
        "brief_id": f"BR-{uuid4().hex[:8].upper()}",
        "company_id": company_id,
        "company_name": company_name,
        "job_id": job_id,
        "job_title": job_title,
        "conversation_type": conversation_type,
        "interview_stage": interview_stage,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "sections": {
            "company_360": company_360,
            "role_intelligence": role_intel,
            "people_power_map": people_ranked,
            "proof_of_work_match": {
                "top_assets": top_proof,
                "top_three_display": top_proof[:3],
                "missing_proof": missing,
            },
            "conversation_script": script,
            "optional_disclosure": disclosure,
            "interview_prep": interview_prep,
            "action_plan": {
                "follow_up": follow_up,
                "next_actions": next_actions,
            },
        },
    }
    return brief


def score_brief_completeness(brief: dict) -> dict:
    """Score brief readiness 0-100 based on section completeness."""
    s = brief.get("sections", {})
    gaps: list[str] = []
    weights = {
        "company_profile": 20,
        "role_reasoning": 20,
        "proof_assets": 20,
        "people_map": 15,
        "script": 15,
        "interview_prep": 10,
    }
    earned = 0

    company = s.get("company_360", {})
    if company.get("found") and company.get("strategic_summary"):
        earned += weights["company_profile"]
    else:
        gaps.append("Company profile incomplete or missing strategic summary")

    role = s.get("role_intelligence", {})
    if role.get("why_role_exists") and role.get("business_problem"):
        earned += weights["role_reasoning"]
    else:
        gaps.append("Role reasoning missing (why role exists / business problem)")

    proof = s.get("proof_of_work_match", {})
    top_assets = proof.get("top_three_display") or proof.get("top_assets") or []
    if len(top_assets) >= 1:
        earned += weights["proof_assets"]
    else:
        gaps.append("No proof assets matched to role/company")

    people = s.get("people_power_map") or []
    if len(people) >= 1:
        earned += weights["people_map"]
    else:
        gaps.append("People map empty — add verified contacts")

    script = s.get("conversation_script", "")
    if script and len(script.strip()) > 50:
        earned += weights["script"]
    else:
        gaps.append("Conversation script not generated")

    prep = s.get("interview_prep", {})
    topic_count = sum(len(prep.get(k, [])) for k in ("technical_topics", "business_topics", "behavioral_topics"))
    if topic_count >= 2:
        earned += weights["interview_prep"]
    else:
        gaps.append("Interview prep topics insufficient")

    return {
        "score": earned,
        "label": "Ready" if earned >= 80 else ("Needs work" if earned >= 50 else "Incomplete"),
        "gaps": gaps,
    }


def export_brief_markdown(brief: dict) -> str:
    """Export conversation brief as professional markdown with TOC and disclaimer."""
    s = brief["sections"]
    company = s["company_360"]
    role = s["role_intelligence"]
    completeness = score_brief_completeness(brief)
    generated = brief.get("created_at", datetime.now().isoformat(timespec="seconds"))

    lines = [
        f"# Conversation Brief: {brief['job_title']} @ {brief['company_name']}",
        "",
        f"**Brief ID:** {brief['brief_id']}  ",
        f"**Conversation Type:** {brief['conversation_type']}  ",
        f"**Interview Stage:** {brief['interview_stage']}  ",
        f"**Generated:** {generated}  ",
        f"**Brief Readiness:** {completeness['score']}% ({completeness['label']})",
        "",
        "> **Disclaimer:** This brief is generated from structured research data and portfolio "
        "mappings. Verify all company, contact, and role details independently before use in "
        "live conversations. Sponsorship signals are indicative only — not legal certainty.",
        "",
        "## Table of Contents",
        "",
        "1. [Company 360](#1-company-360)",
        "2. [Role Intelligence](#2-role-intelligence)",
        "3. [People / Power Map](#3-people--power-map)",
        "4. [Proof-of-Work Match](#4-proof-of-work-match)",
        "5. [Conversation Script](#5-conversation-script)",
        "6. [Optional Sponsorship Disclosure](#6-optional-sponsorship-disclosure)",
        "7. [Interview Prep](#7-interview-prep)",
        "8. [Action Plan](#8-action-plan)",
        "",
        "---",
        "",
        "## 1. Company 360",
        "",
        f"**Industry:** {company.get('industry', 'N/A')}  ",
        f"**DFW Presence:** {company.get('dfw_presence', 'N/A')}  ",
        f"**Priority Tier:** {company.get('priority_tier', 'N/A')}",
        "",
        company.get("strategic_summary", ""),
        "",
        "### Tech Stack Themes",
        "",
    ]
    for theme in company.get("tech_stack_themes", []):
        lines.append(f"- {theme}")

    lines.extend(["", "### Active Project Themes", ""])
    for t in company.get("themes", [])[:5]:
        lines.append(f"- **{t['theme']}** ({t['confidence_level']} confidence)")

    if company.get("research_gaps"):
        lines.extend(["", "### Research Gaps", ""])
        for gap in company["research_gaps"]:
            lines.append(f"- {gap}")

    lines.extend([
        "", "---", "", "## 2. Role Intelligence", "",
        f"**Why this role exists:** {role.get('why_role_exists', '')}", "",
        f"**Business problem:** {role.get('business_problem', '')}", "",
        f"**Likely team:** {role.get('likely_team', '')}", "",
        "### 30/60/90 Day Plan", "",
        f"- **30 days:** {role.get('success_metrics_30', '')}",
        f"- **60 days:** {role.get('success_metrics_60', '')}",
        f"- **90 days:** {role.get('success_metrics_90', '')}",
        "", "### How I Would Help", "",
    ])
    for bullet in role.get("how_i_would_help", []):
        lines.append(f"- {bullet}")

    lines.extend(["", "---", "", "## 3. People / Power Map", ""])
    for person in s["people_power_map"][:5]:
        lines.append(
            f"- **{person.get('person_name', 'TBD')}** ({person.get('contact_type', '')}) — "
            f"priority {person.get('conversation_priority', 0)}, "
            f"status: {person.get('verification_status', 'placeholder')}"
        )

    lines.extend(["", "---", "", "## 4. Proof-of-Work Match", ""])
    for asset in s["proof_of_work_match"].get("top_three_display", []):
        lines.append(f"- **{asset['title']}** (score: {asset['match_score']}) — `{asset['url_or_path']}`")
    if s["proof_of_work_match"].get("missing_proof"):
        lines.extend(["", "### Missing Proof", ""])
        for gap in s["proof_of_work_match"]["missing_proof"]:
            lines.append(f"- {gap}")

    lines.extend([
        "", "---", "", "## 5. Conversation Script", "", s["conversation_script"], "",
        "---", "", "## 6. Optional Sponsorship Disclosure", "", s["optional_disclosure"], "",
        "---", "", "## 7. Interview Prep", "",
    ])
    prep = s.get("interview_prep", {})
    for section in ("technical_topics", "business_topics", "behavioral_topics"):
        topics = prep.get(section, [])
        if topics:
            lines.append(f"### {section.replace('_', ' ').title()}")
            lines.append("")
            for t in topics[:3]:
                lines.append(f"- [{t.get('priority', '')}] {t.get('question', '')}")
            lines.append("")

    lines.extend([
        "---", "", "## 8. Action Plan", "",
        "### Follow-Up Template", "", s["action_plan"]["follow_up"], "",
        "### Next Actions", "",
    ])
    for action in s["action_plan"]["next_actions"]:
        lines.append(f"- [ ] {action}")

    if completeness["gaps"]:
        lines.extend(["", "### Readiness Gaps", ""])
        for gap in completeness["gaps"]:
            lines.append(f"- {gap}")

    lines.extend([
        "",
        "---",
        "",
        f"*Generated by Career Intelligence OS v1.0 — {generated}*",
        "",
        "*Internal use only. Do not distribute without verifying contact and company data.*",
    ])
    return "\n".join(lines)


def save_conversation_brief(brief: dict, markdown: str | None = None) -> str:
    """Append brief metadata to conversation_briefs.csv."""
    markdown = markdown or export_brief_markdown(brief)
    export_dir = DATA_DIR.parent / "exports"
    export_dir.mkdir(exist_ok=True)
    md_path = export_dir / f"{brief['brief_id']}.md"
    md_path.write_text(markdown, encoding="utf-8")

    row = {
        "brief_id": brief["brief_id"],
        "company_id": brief["company_id"],
        "company_name": brief["company_name"],
        "job_id": brief["job_id"],
        "job_title": brief["job_title"],
        "conversation_type": brief["conversation_type"],
        "interview_stage": brief["interview_stage"],
        "contact_type": brief["conversation_type"],
        "created_at": brief["created_at"],
        "status": "saved",
        "markdown_path": str(md_path.relative_to(DATA_DIR.parent)),
        "notes": f"Generated by Interview Command Center",
    }

    if BRIEFS_PATH.exists() and BRIEFS_PATH.stat().st_size > 0:
        df = pd.read_csv(BRIEFS_PATH)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(BRIEFS_PATH, index=False)
    return str(md_path)
