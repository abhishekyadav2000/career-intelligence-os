"""Tests for role demand scorer."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.role_demand_scorer import (
    classify_fit_tier,
    load_role_demand_scores,
    recommend_action,
    score_role_demand,
)


def test_classify_fit_tier():
    assert classify_fit_tier(80) == "A"
    assert classify_fit_tier(60) == "B"
    assert classify_fit_tier(40) == "C"
    assert classify_fit_tier(20) == "D"


def test_recommend_action():
    assert recommend_action("A", 80) == "immediate_outreach"
    assert recommend_action("D", 20) == "ignore"


def test_score_role_demand_dfw():
    job = {
        "job_id": "J0001",
        "company_id": "C001",
        "company_name": "JPMorgan Chase",
        "title": "Technology Analyst",
        "description": "Python SQL cloud security data analytics automation analyst",
        "location": "Plano / Dallas",
        "role_family": "Cloud / Security / Data / AI / Analyst",
        "posted_date": "2026-07-01",
        "job_url": "https://careers.jpmorgan.com",
        "visa_notes": "sponsor signal DOL",
    }
    score = score_role_demand(job, reference=datetime(2026, 7, 6))
    assert score["dfw_score"] == 20
    assert score["recency_score"] == 15
    assert score["total_fit_score"] >= 55
    assert score["fit_tier"] in ("A", "B", "C")


def test_load_role_demand_scores():
    df = load_role_demand_scores()
    assert not df.empty
    assert "fit_tier" in df.columns
    assert len(df) >= 100
