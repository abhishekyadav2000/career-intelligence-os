"""Tests for Mission Control execution layer."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.conversation_brief_generator import generate_opt_disclosure
from src.conversation_feedback_analyzer import (
    SAMPLE_LOG_PATH,
    analyze_conversations,
    load_conversation_log,
)
from src.data_loader import load_all
from src.message_queue_engine import build_message_queue, generate_message_for_card
from src.mission_control_engine import build_mission_control, get_monday_readiness_score
from src.pipeline_engine import (
    assign_pipeline_stage,
    build_pipeline_cards,
    get_pipeline_metrics,
    score_pipeline_card,
)
from src.schedule_engine import (
    get_daily_plan,
    get_next_activities,
    load_activity_schedule,
    load_launch_plan,
    summarize_week_plan,
)


def test_score_pipeline_card_weights():
    score = score_pipeline_card(80, 70, 60, 50, 40, 30)
    expected = 80 * 0.30 + 70 * 0.20 + 60 * 0.15 + 50 * 0.15 + 40 * 0.10 + 30 * 0.10
    assert score == round(expected, 1)


def test_assign_pipeline_stage_placeholder():
    stage, reason = assign_pipeline_stage("network first", "placeholder")
    assert stage == "Person Verification"
    assert "not verified" in reason.lower()


def test_assign_pipeline_stage_skip():
    stage, _ = assign_pipeline_stage("skip/watchlist", "verified")
    assert stage == "Blocked/Skip"


def test_build_pipeline_cards():
    data = load_all()
    cards = build_pipeline_cards(data, reference=datetime(2026, 7, 6))
    assert len(cards) == len(data["jobs"])
    assert all(c["card_id"].startswith("PC-") for c in cards)
    assert cards[0]["priority_score"] >= cards[-1]["priority_score"]


def test_pipeline_metrics():
    data = load_all()
    cards = build_pipeline_cards(data)
    metrics = get_pipeline_metrics(cards)
    assert metrics["total_cards"] == len(cards)
    assert sum(metrics["stage_counts"].values()) == len(cards)


def test_monday_readiness_score():
    data = load_all()
    cards = build_pipeline_cards(data, reference=datetime(2026, 7, 6))
    readiness = get_monday_readiness_score(cards, data, reference=datetime(2026, 7, 6))
    assert 0 <= readiness["total"] <= 100
    assert len(readiness["dimensions"]) == 5
    assert readiness["max"] == 100


def test_build_mission_control():
    data = load_all()
    mc = build_mission_control(data, date=datetime(2026, 7, 6))
    assert "readiness" in mc
    assert "action_queue" in mc
    assert "pipeline_board" in mc
    assert mc["date"] == "2026-07-06"


def test_schedule_engine():
    plan = load_launch_plan()
    assert len(plan) >= 5
    monday = get_daily_plan(datetime(2026, 7, 6), plan)
    assert monday is not None
    assert monday["day_name"] == "Monday"
    schedule = load_activity_schedule()
    assert len(schedule) >= 8
    week = summarize_week_plan(plan)
    assert "monday_focus" in week
    next_acts = get_next_activities(datetime(2026, 7, 6, 8, 0))
    assert len(next_acts) >= 1


def test_message_queue_generation():
    data = load_all()
    cards = build_pipeline_cards(data)
    queue = build_message_queue(cards, data)
    assert isinstance(queue, list)
    if queue:
        draft = generate_message_for_card(queue[0], data)
        assert len(draft) > 50
        assert "OPT/EAD" not in draft or "Optional" in draft


def test_opt_disclosure_wording():
    text = generate_opt_disclosure(include=True)
    assert "OPT/EAD" in text
    assert "STEM OPT pathway" in text
    assert "require employer sponsorship" not in text


def test_conversation_feedback_ignores_sample_rows():
    template_rows = load_conversation_log()
    assert len(template_rows) == 0
    sample_rows = []
    with SAMPLE_LOG_PATH.open(newline="", encoding="utf-8") as handle:
        import csv
        reader = csv.DictReader(handle)
        sample_rows = list(reader)
    assert len(sample_rows) >= 3
    result = analyze_conversations(sample_rows)
    assert result["total_conversations"] == len(sample_rows)
