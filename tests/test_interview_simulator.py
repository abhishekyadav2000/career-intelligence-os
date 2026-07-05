"""Tests for interview_simulator — rule-based mode without API."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_all
from src.interview_simulator import (
    build_simulator_context,
    count_insights_by_company,
    generate_feedback,
    generate_recruiter_question,
    get_round_script,
    load_interview_insights,
    normalize_round,
    save_simulator_session,
)
from src.profile_manager import load_profile


@pytest.fixture(autouse=True)
def no_llm(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)


def test_load_interview_insights_jpmorgan():
    insights = load_interview_insights("C001")
    assert len(insights) >= 5
    for row in insights:
        assert row.get("source_url", "").startswith("http")


def test_normalize_round_aliases():
    assert normalize_round("recruiter screen") == "recruiter_screen"
    assert normalize_round("hiring manager screen") == "hm_screen"
    assert normalize_round("technical interview") == "technical"


def test_get_round_script():
    rounds = get_round_script("JPMorgan Chase", "Technology Analyst")
    assert len(rounds) == 5
    assert rounds[0]["round"] == "recruiter_screen"


def test_rule_based_question_without_llm():
    data = load_all()
    companies = data["companies"]
    jpm = companies[companies["company_name"] == "JPMorgan Chase"].iloc[0]
    jobs = data["jobs"]
    job = jobs[jobs["company_id"] == jpm["company_id"]].iloc[0]
    insights = load_interview_insights(jpm["company_id"], job["role_family"], "recruiter_screen")
    profile = load_profile()
    context = build_simulator_context(
        jpm.to_dict(),
        job.to_dict(),
        profile,
        insights,
        [],
        reasoning_df=data.get("role_reasoning"),
        jobs_df=jobs,
    )
    q = generate_recruiter_question(context, "recruiter_screen", [])
    assert len(q) > 10


def test_rule_based_feedback():
    data = load_all()
    jpm = data["companies"][data["companies"]["company_name"] == "JPMorgan Chase"].iloc[0]
    job = data["jobs"][data["jobs"]["company_id"] == jpm["company_id"]].iloc[0]
    insights = load_interview_insights(jpm["company_id"])
    context = build_simulator_context(
        jpm.to_dict(), job.to_dict(), load_profile(), insights, [],
    )
    fb = generate_feedback(
        "I built a dashboard using Python and SQL that helped prioritize enterprise roles.",
        "Tell me about yourself",
        context,
    )
    assert "Feedback" in fb


def test_count_insights_by_company():
    counts = count_insights_by_company()
    assert counts.get("JPMorgan Chase", 0) >= 5


def test_save_simulator_session(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.interview_simulator.DATA_DIR",
        tmp_path,
    )
    monkeypatch.setattr(
        "src.interview_simulator.SESSIONS_PATH",
        tmp_path / "simulator_sessions.csv",
    )
    sid = save_simulator_session(
        "C001", "JPMorgan Chase", "J0001", "Analyst", "recruiter_screen",
        ["Tell me about yourself"],
        notes="test",
    )
    assert sid.startswith("SIM-")
    assert (tmp_path / "simulator_sessions.csv").exists()
