"""Engagement engine — hooks and message drafts (human-in-the-loop, v1.3)."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ENGAGEMENT_HOOKS_PATH = DATA_DIR / "engagement_hooks.csv"
OUTREACH_QUEUE_PATH = DATA_DIR / "outreach_queue.csv"

HOOK_COLUMNS = [
    "hook_id",
    "company_id",
    "person_id",
    "hook_type",
    "hook_title",
    "hook_content",
    "source_url",
    "topic",
    "suggested_opener",
    "engagement_level",
    "status",
    "last_updated",
]

QUEUE_COLUMNS = [
    "queue_id",
    "company_id",
    "person_id",
    "person_name",
    "person_type",
    "channel",
    "message_type",
    "message_draft",
    "engagement_level",
    "hook_id",
    "status",
    "next_action",
    "scheduled_date",
    "sent_date",
    "notes",
]

DEFAULT_PROFILE = {
    "name": "Abhishek",
    "headline": "Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics",
    "positioning": (
        "DFW-based emerging technology professional with UNT MIS background. "
        "I build decision systems and cloud security evidence — not a generic job seeker."
    ),
    "education": "UNT MIS / enterprise technology focus",
    "location": "Dallas-Fort Worth",
}


def load_engagement_hooks(
    company_id: str | None = None,
    person_id: str | None = None,
    path: Path | None = None,
) -> list[dict]:
    p = path or ENGAGEMENT_HOOKS_PATH
    if not p.exists():
        return []
    df = pd.read_csv(p)
    if company_id and "company_id" in df.columns:
        df = df[df["company_id"] == company_id]
    if person_id and "person_id" in df.columns:
        df = df[df["person_id"] == person_id]
    return df.to_dict("records")


def suggest_engagement_level(person_type: str, hook_type: str) -> int:
    """
    Engagement ladder 1-10 based on person type and hook warmth.
    1=observe, 3=comment, 5=connect, 7=DM, 9=ask for conversation.
    """
    base = {
        "recruiter": 5,
        "hiring_manager": 4,
        "peer_similar_role": 6,
        "dfw_local": 5,
        "alumni_connection": 7,
        "thought_leader": 2,
    }.get(person_type, 4)

    hook_boost = {
        "linkedin_post": 2,
        "company_post": 1,
        "related_job": 3,
        "company_blog": 2,
        "shared_location": 2,
        "shared_school": 3,
        "shared_topic": 2,
    }.get(hook_type, 0)

    return min(10, max(1, base + hook_boost - 2))


def generate_hook_from_signal(signal: dict, role: dict | None, company: dict | None) -> dict:
    """Create an engagement hook from a demand signal."""
    company_id = signal.get("company_id", "")
    signal_type = signal.get("signal_type", "press_release")
    hook_type_map = {
        "job_posting": "related_job",
        "press_release": "company_post",
        "blog_post": "company_blog",
        "hiring_event": "company_post",
        "product_launch": "company_post",
        "webinar": "company_blog",
        "leadership_update": "company_post",
    }
    hook_type = hook_type_map.get(signal_type, "company_post")
    role_title = (role or {}).get("job_title", (role or {}).get("title", "technology role"))
    company_name = signal.get("company_name", (company or {}).get("company_name", "the company"))

    opener = (
        f"I noticed {company_name}'s recent focus on {signal.get('technology_area', 'platform modernization')} — "
        f"my work on governed automation and cloud security evidence aligns with that direction."
    )

    return {
        "hook_id": f"HK-{signal.get('signal_id', 'NEW')}",
        "company_id": company_id,
        "person_id": "",
        "hook_type": hook_type,
        "hook_title": signal.get("signal_title", "Company signal"),
        "hook_content": signal.get("notes", signal.get("signal_title", "")),
        "source_url": signal.get("source_url", ""),
        "topic": signal.get("technology_area", ""),
        "suggested_opener": opener,
        "engagement_level": suggest_engagement_level("peer_similar_role", hook_type),
        "status": "available",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }


def generate_message_draft(
    person: dict,
    hook: dict,
    message_type: str,
    profile: dict | None = None,
) -> str:
    """Generate copy-ready outreach draft — value-first, not begging."""
    if profile:
        prof = profile
    else:
        try:
            from src.profile_manager import load_profile
            prof = load_profile()
        except Exception:
            prof = DEFAULT_PROFILE

    name = prof.get("name", "[YOUR NAME]")
    company = person.get("company_name", hook.get("company_name", "your team"))
    person_type = person.get("person_type", "recruiter")
    hook_title = hook.get("hook_title", "recent technology initiatives")
    topic = hook.get("topic", "cloud security and automation")
    opener = hook.get("suggested_opener", "")
    net_pos = prof.get("networking_positioning", "")
    location = prof.get("location", "DFW")
    headline = prof.get("headline", "enterprise technology")
    bullets = prof.get("experience_bullets", [])
    proof_hint = bullets[0] if bullets else "portfolio proof aligned to your technology direction"

    identity = net_pos if net_pos and not net_pos.startswith("[") else (
        f"I'm {name}, a {location}-based professional focused on {headline}."
    )

    templates = {
        "comment_on_post": (
            f"Strong perspective on {topic}. {identity} "
            f"I build similar patterns — especially around audit-ready controls and measurable outcomes. "
            f"Would enjoy learning how {company} approaches this at scale."
        ),
        "connection_request": (
            f"Hi — {identity} "
            f"I saw {hook_title} and thought it connected to work I've done ({proof_hint}). "
            f"Would value connecting."
        ),
        "dm_after_connection": (
            f"Thanks for connecting. I noticed {company}'s work on {topic} — "
            f"{proof_hint}. Happy to share a brief walkthrough "
            f"if useful for your {person_type.replace('_', ' ')} network."
        ),
        "feedback_ask": (
            f"I'm exploring {topic} roles at {company} in {location}. "
            f"Not asking for a referral — I'd appreciate 10 minutes of feedback on whether my "
            f"portfolio proof reads credible for teams like yours."
        ),
        "soft_role_bridge": (
            f"{opener or ('I followed ' + company + chr(39) + 's recent signal on ' + topic + '.')} "
            f"{identity} "
            f"Open to a brief conversation if timing aligns."
        ),
    }
    return templates.get(message_type, templates["connection_request"])


def load_outreach_queue(company_id: str | None = None, path: Path | None = None) -> list[dict]:
    p = path or OUTREACH_QUEUE_PATH
    if not p.exists():
        return []
    df = pd.read_csv(p)
    if company_id and "company_id" in df.columns:
        df = df[df["company_id"] == company_id]
    return df.to_dict("records")


def save_outreach_queue(rows: list[dict], path: Path | None = None) -> Path:
    p = path or OUTREACH_QUEUE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in QUEUE_COLUMNS})
    return p
