"""Tests for demand intelligence engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.demand_intelligence_engine import (
    get_company_demand_summary,
    get_recent_hiring_signals,
    load_demand_signals,
)


def test_load_demand_signals_jpmorgan():
    df = load_demand_signals("C001")
    assert not df.empty
    assert "signal_type" in df.columns
    assert "source_url" in df.columns


def test_recent_hiring_signals():
    recent = get_recent_hiring_signals("C001", days=30)
    assert isinstance(recent, list)


def test_company_demand_summary():
    summary = get_company_demand_summary("C001")
    assert summary["company_id"] == "C001"
    assert summary["total_signals"] > 0
    assert "tier_a_roles" in summary
