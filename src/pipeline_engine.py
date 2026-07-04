"""Pipeline card engine — execution queue on top of intelligence data."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pandas as pd

from src.company_priority_scorer import score_companies
from src.data_confidence import compute_confidence, is_stale
from src.people_power_mapper import load_people_map, rank_contacts_for_conversation
from src.proof_asset_mapper import get_top_proof_assets_for_display, load_proof_assets
from src.recommendation_engine import recommend_batch
from src.role_fit_scorer import score_jobs_dataframe

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PIPELINE_CARDS_PATH = DATA_DIR / "pipeline_cards.csv"

PIPELINE_STAGES = [
    "Research Needed",
    "Person Verification",
    "Ready to Contact",
    "Message Sent",
    "Applied",
    "Interviewing",
    "Follow-Up Due",
    "Blocked/Skip",
]

PIPELINE_CARD_COLUMNS = [
    "card_id",
    "job_id",
    "company_id",
    "company_name",
    "job_title",
    "person_id",
    "person_name",
    "contact_type",
    "pipeline_stage",
    "priority_score",
    "fit_score",
    "company_priority_score",
    "sponsorship_score",
    "proof_score",
    "people_verification_score",
    "urgency_score",
    "recommendation_action",
    "next_action",
    "proof_asset_id",
    "proof_asset_title",
    "follow_up_date",
    "last_updated",
    "data_confidence",
    "blocked_reason",
    "notes",
]

PRIORITY_WEIGHTS = {
    "fit": 0.30,
    "company": 0.20,
    "sponsorship": 0.15,
    "proof": 0.15,
    "people_verification": 0.10,
    "urgency": 0.10,
}


def _verification_score(status: str) -> float:
    mapping = {
        "verified": 100,
        "verified_public": 95,
        "partial": 70,
        "needs_verification": 40,
        "placeholder": 15,
    }
    return float(mapping.get((status or "placeholder").lower().strip(), 20))


def score_pipeline_card(
    fit_score: float,
    company_score: float,
    sponsorship_score: float,
    proof_score: float,
    people_verification_score: float,
    urgency_score: float,
) -> float:
    """Weighted priority score (0–100)."""
    return round(
        fit_score * PRIORITY_WEIGHTS["fit"]
        + company_score * PRIORITY_WEIGHTS["company"]
        + sponsorship_score * PRIORITY_WEIGHTS["sponsorship"]
        + proof_score * PRIORITY_WEIGHTS["proof"]
        + people_verification_score * PRIORITY_WEIGHTS["people_verification"]
        + urgency_score * PRIORITY_WEIGHTS["urgency"],
        1,
    )


def assign_pipeline_stage(
    recommendation_action: str,
    verification_status: str,
    follow_up_date: str = "",
    outreach_status: str = "",
    reference: datetime | None = None,
) -> tuple[str, str]:
    """Return (pipeline_stage, blocked_reason)."""
    ref = reference or datetime.now()
    action = (recommendation_action or "").lower()
    status = (verification_status or "placeholder").lower()
    outreach = (outreach_status or "").lower()

    if action == "skip/watchlist":
        return "Blocked/Skip", "Recommendation: skip/watchlist"

    if status == "placeholder":
        if action == "research more":
            return "Research Needed", ""
        return "Person Verification", "Contact not verified"

    if follow_up_date:
        fu = None
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                fu = datetime.strptime(follow_up_date[:10], fmt)
                break
            except ValueError:
                continue
        if fu and fu.date() <= ref.date():
            return "Follow-Up Due", ""

    if outreach in ("applied", "application submitted"):
        return "Applied", ""
    if outreach in ("sent", "message sent", "replied"):
        return "Message Sent", ""
    if outreach in ("scheduled", "interviewing", "interview scheduled"):
        return "Interviewing", ""

    if action == "apply now" and status in ("verified", "verified_public", "partial"):
        return "Ready to Contact", ""
    if action == "network first":
        return "Ready to Contact", ""
    if action == "research more":
        return "Research Needed", ""

    return "Person Verification", ""


def _best_contact(company_id: str, people_df: pd.DataFrame) -> dict:
    ranked = rank_contacts_for_conversation(
        company_id, "recruiter", "initial outreach", people_df
    )
    if ranked:
        return ranked[0]
    subset = people_df[people_df["company_id"] == company_id]
    if subset.empty:
        return {}
    row = subset.iloc[0]
    return row.to_dict()


def _urgency_score(recommendation_action: str, fit_score: float) -> float:
    action = (recommendation_action or "").lower()
    if action == "apply now":
        return min(100, fit_score + 20)
    if action == "network first":
        return min(90, fit_score + 10)
    if action == "research more":
        return 50
    return 25


def build_pipeline_cards(data: dict, reference: datetime | None = None) -> list[dict]:
    """Build pipeline cards from loaded intelligence data."""
    ref = reference or datetime.now()
    jobs_df = data["jobs"]
    companies_df = data["companies"]
    contacts_df = data["contacts"]
    people_df = data.get("people_map", load_people_map())
    proof_df = data.get("proof_assets", load_proof_assets())
    profiles_df = data.get("company_profiles", pd.DataFrame())
    sources_df = data.get("research_sources", pd.DataFrame())

    scores = score_jobs_dataframe(jobs_df, companies_df)
    company_scores = score_companies(companies_df, jobs_df, contacts_df)
    recommendations = recommend_batch(scores, company_scores)

    rec_map = {r["job_id"]: r for r in recommendations}
    company_map = {c["company"]: c["priority_score"] for c in company_scores}
    score_map = {s["job_id"]: s for s in scores}

    cards: list[dict] = []
    for _, job in jobs_df.iterrows():
        job_id = job["job_id"]
        company_id = job["company_id"]
        company_name = job["company_name"]
        rec = rec_map.get(job_id, {})
        score = score_map.get(job_id, {})
        fit = float(score.get("fit_score", 0))
        cats = score.get("category_scores", {})
        sponsor = float(cats.get("sponsorship_signal", 50))
        company_pri = float(company_map.get(company_name, 50))

        contact = _best_contact(company_id, people_df)
        person_id = contact.get("person_id", "")
        person_name = contact.get("person_name", "TBD")
        contact_type = contact.get("contact_type", "recruiter")
        verification = contact.get("verification_status", "placeholder")

        top_proof = get_top_proof_assets_for_display(
            job_id, company_id, proof_df, jobs_df, profiles_df, n=1
        )
        proof_asset = top_proof[0] if top_proof else {}
        proof_score = float(proof_asset.get("match_score", 0)) * 10 if proof_asset else 30
        proof_score = min(100, proof_score)
        people_v = _verification_score(verification)

        action = rec.get("action", "research more")
        urgency = _urgency_score(action, fit)
        priority = score_pipeline_card(fit, company_pri, sponsor, proof_score, people_v, urgency)

        has_sources = (
            not sources_df.empty
            and len(sources_df[sources_df["company_id"] == company_id]) > 0
        )
        prof_row = profiles_df[profiles_df["company_id"] == company_id]
        last_updated = prof_row.iloc[0]["last_updated"] if not prof_row.empty else ""
        confidence = compute_confidence(verification, last_updated, has_sources, reference=ref)

        stage, blocked = assign_pipeline_stage(action, verification, reference=ref)
        if confidence == "stale" and stage == "Ready to Contact":
            stage = "Research Needed"
            blocked = blocked or "Stale company profile"

        next_action = _next_action_for_stage(stage, action, contact_type, proof_asset.get("title", ""))

        cards.append({
            "card_id": f"PC-{job_id}",
            "job_id": job_id,
            "company_id": company_id,
            "company_name": company_name,
            "job_title": job["title"],
            "person_id": person_id,
            "person_name": person_name,
            "contact_type": contact_type,
            "pipeline_stage": stage,
            "priority_score": priority,
            "fit_score": fit,
            "company_priority_score": company_pri,
            "sponsorship_score": sponsor,
            "proof_score": proof_score,
            "people_verification_score": people_v,
            "urgency_score": urgency,
            "recommendation_action": action,
            "next_action": next_action,
            "proof_asset_id": proof_asset.get("asset_id", ""),
            "proof_asset_title": proof_asset.get("title", ""),
            "follow_up_date": "",
            "last_updated": ref.strftime("%Y-%m-%d"),
            "data_confidence": confidence,
            "blocked_reason": blocked,
            "notes": rec.get("rationale", ""),
        })

    cards.sort(key=lambda c: c["priority_score"], reverse=True)
    return cards


def _next_action_for_stage(stage: str, action: str, contact_type: str, proof_title: str) -> str:
    proof_ref = proof_title or "top proof asset"
    actions = {
        "Research Needed": "Complete company 360 research and add research_sources",
        "Person Verification": f"Verify {contact_type} contact via public sources before outreach",
        "Ready to Contact": f"Draft outreach with {proof_ref}; export message from queue",
        "Message Sent": "Log conversation in conversation_log_template.csv",
        "Applied": "Track application status; prepare interview packet",
        "Interviewing": "Generate conversation brief and review proof assets",
        "Follow-Up Due": "Send follow-up message; update follow_up_date",
        "Blocked/Skip": "Deprioritize unless market signal changes",
    }
    return actions.get(stage, action)


def load_pipeline_cards(path: Path | None = None) -> list[dict]:
    p = path or PIPELINE_CARDS_PATH
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_pipeline_cards(cards: list[dict], path: Path | None = None) -> Path:
    p = path or PIPELINE_CARDS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PIPELINE_CARD_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for card in cards:
            writer.writerow({col: card.get(col, "") for col in PIPELINE_CARD_COLUMNS})
    return p


def get_today_queue(cards: list[dict], limit: int = 15) -> list[dict]:
    active_stages = {
        "Research Needed",
        "Person Verification",
        "Ready to Contact",
        "Follow-Up Due",
    }
    queue = [c for c in cards if c.get("pipeline_stage") in active_stages]
    queue.sort(key=lambda c: float(c.get("priority_score", 0)), reverse=True)
    return queue[:limit]


def get_follow_up_due(cards: list[dict], reference: datetime | None = None) -> list[dict]:
    ref = reference or datetime.now()
    due = []
    for card in cards:
        if card.get("pipeline_stage") == "Follow-Up Due":
            due.append(card)
            continue
        fu = card.get("follow_up_date", "")
        if not fu:
            continue
        try:
            fu_date = datetime.strptime(fu[:10], "%Y-%m-%d").date()
            if fu_date <= ref.date():
                due.append(card)
        except ValueError:
            continue
    return due


def get_blocked_cards(cards: list[dict]) -> list[dict]:
    return [
        c for c in cards
        if c.get("pipeline_stage") == "Blocked/Skip" or c.get("blocked_reason")
    ]


def get_pipeline_metrics(cards: list[dict]) -> dict:
    stage_counts: dict[str, int] = {s: 0 for s in PIPELINE_STAGES}
    for card in cards:
        stage = card.get("pipeline_stage", "Research Needed")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    priorities = [float(c.get("priority_score", 0)) for c in cards]
    return {
        "total_cards": len(cards),
        "stage_counts": stage_counts,
        "avg_priority": round(sum(priorities) / len(priorities), 1) if priorities else 0,
        "ready_to_contact": stage_counts.get("Ready to Contact", 0),
        "follow_up_due": len(get_follow_up_due(cards)),
        "blocked": stage_counts.get("Blocked/Skip", 0),
    }
