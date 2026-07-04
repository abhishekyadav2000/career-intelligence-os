"""Message queue engine — copy-ready outreach drafts, no auto-send."""

from __future__ import annotations

import csv
from pathlib import Path

from src.conversation_brief_generator import generate_conversation_script
from src.outreach_angle_generator import generate_outreach_batch
from src.role_reasoning_engine import build_role_deep_dive, load_role_reasoning

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MESSAGE_QUEUE_PATH = DATA_DIR / "message_queue.csv"

MESSAGE_COLUMNS = [
    "message_id",
    "card_id",
    "company_name",
    "job_title",
    "contact_type",
    "person_name",
    "pipeline_stage",
    "message_draft",
    "proof_asset_title",
    "status",
    "priority_score",
]


def generate_message_for_card(card: dict, data: dict) -> str:
    """Generate a copy-ready message draft for a pipeline card."""
    jobs_df = data["jobs"]
    job_id = card.get("job_id", "")
    company_name = card.get("company_name", "")
    job_title = card.get("job_title", "")
    contact_type = card.get("contact_type", "recruiter")
    proof_title = card.get("proof_asset_title", "my portfolio projects")

    reasoning_df = data.get("role_reasoning", load_role_reasoning())
    role_reason = build_role_deep_dive(job_id, jobs_df, reasoning_df) if job_id else {}

    script = generate_conversation_script(
        company_name,
        job_title,
        contact_type,
        "initial outreach",
        role_reason,
        [{"title": proof_title}],
    )

    opt_note = (
        "\n\n[Optional — add if asked about work authorization: "
        "I'm currently authorized to work in the U.S. on OPT/EAD and targeting roles "
        "aligned with my STEM OPT pathway.]"
    )
    return script + opt_note


def build_message_queue(cards: list[dict], data: dict) -> list[dict]:
    """Build message queue from pipeline cards ready for outreach."""
    queue = []
    for card in cards:
        stage = card.get("pipeline_stage", "")
        if stage not in ("Ready to Contact", "Person Verification", "Follow-Up Due"):
            continue
        if float(card.get("people_verification_score", 0)) < 40 and stage != "Follow-Up Due":
            continue
        draft = generate_message_for_card(card, data)
        queue.append({
            "message_id": f"MQ-{card.get('card_id', '')}",
            "card_id": card.get("card_id", ""),
            "company_name": card.get("company_name", ""),
            "job_title": card.get("job_title", ""),
            "contact_type": card.get("contact_type", ""),
            "person_name": card.get("person_name", ""),
            "pipeline_stage": stage,
            "message_draft": draft,
            "proof_asset_title": card.get("proof_asset_title", ""),
            "status": "ready" if stage == "Ready to Contact" else "draft",
            "priority_score": card.get("priority_score", 0),
        })
    queue.sort(key=lambda m: float(m.get("priority_score", 0)), reverse=True)
    return queue


def get_messages_ready_to_send(queue: list[dict]) -> list[dict]:
    return [m for m in queue if m.get("status") == "ready"]


def export_message_queue_csv(queue: list[dict], path: Path | None = None) -> Path:
    p = path or MESSAGE_QUEUE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MESSAGE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for msg in queue:
            writer.writerow({col: msg.get(col, "") for col in MESSAGE_COLUMNS})
    return p


def export_message_queue_markdown(queue: list[dict]) -> str:
    lines = ["# Message Queue", ""]
    for i, msg in enumerate(queue, 1):
        lines.extend([
            f"## {i}. {msg.get('company_name')} — {msg.get('job_title')}",
            f"**Contact:** {msg.get('person_name')} ({msg.get('contact_type')})",
            f"**Status:** {msg.get('status')}",
            "",
            msg.get("message_draft", ""),
            "",
            "---",
            "",
        ])
    return "\n".join(lines)
