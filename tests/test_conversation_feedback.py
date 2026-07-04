"""Tests for conversation feedback analyzer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.conversation_feedback_analyzer import analyze_conversations, load_conversation_log


def test_empty_analysis():
    result = analyze_conversations([])
    assert result["total_conversations"] == 0
    assert "No conversation data" in result["summary"]


def test_warm_companies_detected():
    rows = [
        {
            "company": "Capital One",
            "person_type": "recruiter",
            "response": "interested",
            "insight_gained": "",
            "portfolio_gap": "",
            "next_action": "Follow up",
            "follow_up_date": "2026-04-01",
        },
        {
            "company": "Citi",
            "person_type": "hiring_manager",
            "response": "declined",
            "insight_gained": "",
            "portfolio_gap": "",
            "next_action": "",
            "follow_up_date": "",
        },
    ]
    result = analyze_conversations(rows)
    assert result["total_conversations"] == 2
    assert "Capital One" in result["warm_companies"]
    assert "Citi" in result["cold_companies"]


def test_skill_gaps_and_objections():
    rows = [
        {
            "company": "JPMorgan Chase",
            "person_type": "recruiter",
            "response": "replied",
            "insight_gained": "Asked about sponsorship and H-1B timeline",
            "portfolio_gap": "Cloud / IAM / SIEM lab",
            "next_action": "Send demo link",
            "follow_up_date": "2026-04-01",
        },
    ]
    result = analyze_conversations(rows)
    assert result["skill_gaps"][0]["gap"] == "Cloud / IAM / SIEM lab"
    assert any("Sponsorship" in o["objection"] for o in result["repeated_objections"])


def test_load_template_empty_by_default():
    rows = load_conversation_log()
    assert len(rows) == 0


def test_sample_log_loads_when_explicit():
    from src.conversation_feedback_analyzer import SAMPLE_LOG_PATH
    import csv
    with SAMPLE_LOG_PATH.open(newline="", encoding="utf-8") as handle:
        sample_rows = list(csv.DictReader(handle))
    assert len(sample_rows) >= 3
