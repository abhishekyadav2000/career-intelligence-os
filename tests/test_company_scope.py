"""Tests for company-scoped focus mode and action queue filtering."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_all
from src.mission_control_engine import build_mission_control, get_action_queue
from src.pipeline_engine import (
    build_pipeline_cards,
    filter_cards_by_company,
    get_today_queue,
    load_pipeline_cards,
)


@pytest.fixture
def pipeline_data():
    data = load_all()
    cards = load_pipeline_cards() or build_pipeline_cards(data, reference=datetime(2026, 7, 6))
    return data, cards


def test_action_queue_filtered_by_company_id(pipeline_data):
    data, cards = pipeline_data
    jpm_id = "C001"
    queue = get_action_queue(cards, company_id=jpm_id, limit=50)
    assert queue, "Expected at least one JPMorgan action"
    assert all(c.get("company_id") == jpm_id for c in queue)


def test_get_today_queue_no_mixed_companies_when_focused(pipeline_data):
    _, cards = pipeline_data
    citi_id = "C004"
    queue = get_today_queue(cards, company_id=citi_id, limit=50)
    companies = {c.get("company_id") for c in queue}
    assert companies == {citi_id} or companies <= {citi_id}


def test_focus_mode_filters_pipeline_board(pipeline_data):
    data, _ = pipeline_data
    mc = build_mission_control(
        data,
        date=datetime(2026, 7, 6),
        company_id="C001",
        focus_mode=True,
    )
    board_cards = [c for stage in mc["pipeline_board"].values() for c in stage]
    assert board_cards
    assert all(c.get("company_id") == "C001" for c in board_cards)


def test_portfolio_mode_includes_multiple_companies(pipeline_data):
    data, _ = pipeline_data
    mc = build_mission_control(
        data,
        date=datetime(2026, 7, 6),
        company_id="C001",
        focus_mode=False,
    )
    board_cards = [c for stage in mc["pipeline_board"].values() for c in stage]
    company_ids = {c.get("company_id") for c in board_cards}
    assert len(company_ids) > 1


def test_filter_cards_by_company(pipeline_data):
    _, cards = pipeline_data
    filtered = filter_cards_by_company(cards, "C002")
    assert filtered
    assert all(c.get("company_id") == "C002" for c in filtered)
