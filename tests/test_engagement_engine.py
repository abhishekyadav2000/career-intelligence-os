"""Tests for engagement engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engagement_engine import (
    generate_hook_from_signal,
    generate_message_draft,
    load_engagement_hooks,
    suggest_engagement_level,
)


def test_suggest_engagement_level():
    assert 1 <= suggest_engagement_level("recruiter", "related_job") <= 10
    assert suggest_engagement_level("alumni_connection", "shared_school") >= 5


def test_generate_hook_from_signal():
    signal = {
        "signal_id": "DS-TEST",
        "company_id": "C001",
        "company_name": "JPMorgan Chase",
        "signal_type": "job_posting",
        "signal_title": "Test Role",
        "technology_area": "Cloud Security",
        "source_url": "https://careers.jpmorgan.com",
        "notes": "Test signal",
    }
    hook = generate_hook_from_signal(signal, None, None)
    assert hook["hook_type"] == "related_job"
    assert "JPMorgan" in hook["suggested_opener"]


def test_generate_message_draft_not_job_seeker():
    person = {"company_name": "JPMorgan Chase", "person_type": "recruiter"}
    hook = {"hook_title": "AI productivity", "topic": "automation", "suggested_opener": "Test"}
    draft = generate_message_draft(person, hook, "connection_request")
    assert "job seeker" not in draft.lower()
    assert "DFW" in draft or "UNT" in draft


def test_load_engagement_hooks_jpm():
    hooks = load_engagement_hooks("C001")
    assert len(hooks) >= 1
