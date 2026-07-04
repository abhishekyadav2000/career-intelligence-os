"""Mission Control engine — Monday-ready execution dashboard."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.conversation_feedback_analyzer import load_conversation_log
from src.data_confidence import get_confidence_warnings, is_stale
from src.message_queue_engine import build_message_queue
from src.pipeline_engine import (
    PIPELINE_STAGES,
    build_pipeline_cards,
    get_blocked_cards,
    get_follow_up_due,
    get_pipeline_metrics,
    get_today_queue,
    load_pipeline_cards,
)
from src.schedule_engine import (
    get_daily_plan,
    get_next_activities,
    get_overdue_activities,
    load_activity_schedule,
    load_launch_plan,
    summarize_week_plan,
)


def get_top_targets(cards: list[dict], limit: int = 10) -> list[dict]:
    active = [
        c for c in cards
        if c.get("pipeline_stage") not in ("Blocked/Skip",)
    ]
    active.sort(key=lambda c: float(c.get("priority_score", 0)), reverse=True)
    return active[:limit]


def get_action_queue(cards: list[dict], limit: int = 15) -> list[dict]:
    return get_today_queue(cards, limit=limit)


def get_pipeline_board(cards: list[dict]) -> dict[str, list[dict]]:
    board = {stage: [] for stage in PIPELINE_STAGES}
    for card in cards:
        stage = card.get("pipeline_stage", "Research Needed")
        if stage not in board:
            stage = "Research Needed"
        board[stage].append(card)
    for stage in board:
        board[stage].sort(key=lambda c: float(c.get("priority_score", 0)), reverse=True)
    return board


def get_monday_readiness_score(
    cards: list[dict],
    data: dict,
    reference: datetime | None = None,
) -> dict:
    """
    Readiness score: 5 dimensions × 20 points = 100 max.
    1. Pipeline coverage (top targets have cards)
    2. Contact verification readiness
    3. Proof assets linked
    4. Research / brief readiness
    5. Launch plan & schedule alignment
    """
    ref = reference or datetime.now()
    scores: dict[str, int] = {}

    active = [c for c in cards if c.get("pipeline_stage") != "Blocked/Skip"]
    scores["pipeline_coverage"] = min(20, int(len(active) / max(len(cards), 1) * 20)) if cards else 0

    verified = sum(1 for c in cards if float(c.get("people_verification_score", 0)) >= 70)
    scores["contact_verification"] = min(20, int(verified / max(len(cards), 1) * 20)) if cards else 0

    with_proof = sum(1 for c in cards if c.get("proof_asset_title"))
    scores["proof_assets"] = min(20, int(with_proof / max(len(cards), 1) * 20)) if cards else 0

    profiles_df = data.get("company_profiles", pd.DataFrame())
    sources_df = data.get("research_sources", pd.DataFrame())
    fresh_profiles = 0
    if not profiles_df.empty:
        for _, row in profiles_df.iterrows():
            if not is_stale(row.get("last_updated", ""), reference=ref):
                fresh_profiles += 1
    has_sources = not sources_df.empty and len(sources_df) > 0
    research_pts = 0
    if profiles_df.empty:
        research_pts = 0
    else:
        research_pts = int(fresh_profiles / len(profiles_df) * 15)
    if has_sources:
        research_pts += 5
    scores["research_briefs"] = min(20, research_pts)

    plan = get_daily_plan(ref, load_launch_plan())
    schedule = load_activity_schedule()
    schedule_pts = 10 if plan else 0
    monday_acts = [a for a in schedule if a.get("day_of_week", "").lower() == "monday"]
    if monday_acts:
        schedule_pts += min(10, len(monday_acts))
    scores["launch_plan"] = min(20, schedule_pts)

    total = sum(scores.values())
    label = "Ready" if total >= 80 else "Almost Ready" if total >= 60 else "Needs Prep"

    return {
        "total": total,
        "max": 100,
        "label": label,
        "dimensions": scores,
    }


def get_execution_warnings(cards: list[dict], data: dict, reference: datetime | None = None) -> list[str]:
    ref = reference or datetime.now()
    warnings: list[str] = []

    blocked = get_blocked_cards(cards)
    if blocked:
        warnings.append(f"{len(blocked)} pipeline cards blocked or skipped.")

    follow_ups = get_follow_up_due(cards, reference=ref)
    if follow_ups:
        warnings.append(f"{len(follow_ups)} follow-ups due today or overdue.")

    placeholders = sum(
        1 for c in cards
        if c.get("data_confidence") == "placeholder"
    )
    if placeholders > len(cards) * 0.5:
        warnings.append(f"{placeholders} cards rely on placeholder contacts — verify before outreach.")

    stale = sum(1 for c in cards if c.get("data_confidence") == "stale")
    if stale:
        warnings.append(f"{stale} cards have stale company profiles (>30 days).")

    sources_df = data.get("research_sources", pd.DataFrame())
    profiles_df = data.get("company_profiles", pd.DataFrame())
    people_df = data.get("people_map", pd.DataFrame())
    icc_ids = profiles_df["company_id"].tolist()[:5] if not profiles_df.empty else []
    for cid in icc_ids:
        for w in get_confidence_warnings(cid, profiles_df, people_df, sources_df, reference=ref):
            if w not in warnings:
                warnings.append(w)

    conv_rows = load_conversation_log()
    if not conv_rows:
        warnings.append("No real conversations logged — use conversation_log_template.csv after outreach.")

    return warnings


def build_mission_control(data: dict, date: datetime | str | None = None) -> dict:
    """Build full Mission Control payload for dashboard."""
    ref = date if isinstance(date, datetime) else datetime.now()
    if isinstance(date, str):
        try:
            ref = datetime.strptime(date[:10], "%Y-%m-%d")
        except ValueError:
            ref = datetime.now()

    saved = load_pipeline_cards()
    cards = saved if saved else build_pipeline_cards(data, reference=ref)

    metrics = get_pipeline_metrics(cards)
    readiness = get_monday_readiness_score(cards, data, reference=ref)
    top_targets = get_top_targets(cards)
    action_queue = get_action_queue(cards)
    board = get_pipeline_board(cards)
    warnings = get_execution_warnings(cards, data, reference=ref)
    message_queue = build_message_queue(cards, data)
    daily_plan = get_daily_plan(ref)
    week_plan = summarize_week_plan()
    next_activities = get_next_activities(ref)
    overdue = get_overdue_activities(ref)

    top_target = top_targets[0] if top_targets else {}

    return {
        "date": ref.strftime("%Y-%m-%d"),
        "readiness": readiness,
        "metrics": metrics,
        "top_target": top_target,
        "top_targets": top_targets,
        "action_queue": action_queue,
        "pipeline_board": board,
        "follow_up_radar": get_follow_up_due(cards, reference=ref),
        "blockers": get_blocked_cards(cards),
        "warnings": warnings,
        "message_queue": message_queue,
        "daily_plan": daily_plan,
        "week_plan": week_plan,
        "next_activities": next_activities,
        "overdue_activities": overdue,
        "cards": cards,
        "briefs_ready": sum(1 for c in cards if c.get("proof_asset_title")),
    }
