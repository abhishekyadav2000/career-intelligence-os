"""Tests for Interview Command Center modules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.company_profile_engine import (
    build_company_360,
    get_company_research_gaps,
    summarize_company_themes,
)
from src.conversation_brief_generator import (
    export_brief_markdown,
    generate_conversation_brief,
    generate_conversation_script,
    generate_next_action,
    score_brief_completeness,
)
from src.data_loader import load_all
from src.people_power_mapper import (
    build_people_map,
    generate_people_search_queries,
    rank_contacts_for_conversation,
    score_contact_priority,
)
from src.proof_asset_mapper import get_top_proof_assets_for_display, load_proof_assets
from src.role_reasoning_engine import infer_role_reason, build_role_deep_dive


def test_build_company_360_jpmorgan():
    data = load_all()
    profile = build_company_360("C001", data["company_profiles"], data["company_projects"], data["research_sources"], data["people_map"])
    assert profile["found"] is True
    assert profile["company_name"] == "JPMorgan Chase"
    assert len(profile["themes"]) >= 3
    assert profile["people_count"] >= 1


def test_summarize_company_themes():
    data = load_all()
    themes = summarize_company_themes(data["company_projects"], "C001")
    assert len(themes) >= 3
    assert themes[0]["confidence_level"] in ("high", "medium", "low")


def test_research_gaps_no_placeholders():
    data = load_all()
    gaps = get_company_research_gaps("C001", data["company_profiles"], data["people_map"], data["research_sources"])
    assert not any("TBD" in g for g in gaps)
    assert not any("placeholder" in g.lower() for g in gaps)


def test_score_contact_priority_hiring_manager():
    row = {
        "hiring_power_score": 85,
        "contact_type": "hiring_manager",
        "verification_status": "verified_public",
    }
    score = score_contact_priority(row, "hiring manager", "hiring manager screen")
    assert score > 50


def test_hiring_manager_beats_peer_for_hm_conversation():
    hm = score_contact_priority(
        {"hiring_power_score": 80, "contact_type": "hiring_manager", "verification_status": "verified_public"},
        "hiring manager", "hiring manager screen",
    )
    peer = score_contact_priority(
        {"hiring_power_score": 80, "contact_type": "peer", "verification_status": "source_backed"},
        "hiring manager", "hiring manager screen",
    )
    assert hm > peer


def test_build_people_map():
    data = load_all()
    people = build_people_map("C001", data["people_map"])
    assert len(people) >= 1
    assert not any("TBD" in str(n) for n in people["person_name"])
    assert not any(s == "placeholder" for s in people["verification_status"])


def test_people_search_query_url():
    url = generate_people_search_queries("JPMorgan Chase", "recruiter")
    assert "linkedin.com" in url
    assert "JPMorgan" in url


def test_rank_contacts_for_conversation():
    data = load_all()
    ranked = rank_contacts_for_conversation("C001", "hiring manager", "hiring manager screen", data["people_map"])
    assert len(ranked) >= 1
    assert ranked[0]["conversation_priority"] >= ranked[-1]["conversation_priority"]


def test_infer_role_reason_seeded():
    data = load_all()
    reason = infer_role_reason("J0001", data["jobs"], data["role_reasoning"])
    assert reason["found"] is True
    assert "why_role_exists" in reason
    assert len(reason["priority_questions"]) >= 2


def test_role_deep_dive():
    data = load_all()
    dive = build_role_deep_dive("J0003", data["jobs"], data["role_reasoning"])
    assert "plan_30_60_90" in dive
    assert dive["plan_30_60_90"]["30_days"]


def test_proof_assets_top_three():
    data = load_all()
    proof = load_proof_assets()
    top3 = get_top_proof_assets_for_display("J0001", "C001", proof, data["jobs"], data["company_profiles"], n=3)
    assert len(top3) == 3
    assert top3[0]["match_score"] >= top3[-1]["match_score"]


def test_generate_conversation_brief_full():
    data = load_all()
    brief = generate_conversation_brief(
        "C001", "J0001", data["jobs"],
        conversation_type="hiring manager",
        interview_stage="hiring manager screen",
    )
    assert brief["brief_id"].startswith("BR-")
    sections = brief["sections"]
    assert "company_360" in sections
    assert "role_intelligence" in sections
    assert "people_power_map" in sections
    assert "proof_of_work_match" in sections
    assert "conversation_script" in sections
    assert "interview_prep" in sections
    assert "action_plan" in sections
    assert len(sections["proof_of_work_match"]["top_three_display"]) <= 3


def test_export_brief_markdown():
    data = load_all()
    brief = generate_conversation_brief("C001", "J0001", data["jobs"], "hiring manager", "hiring manager screen")
    md = export_brief_markdown(brief)
    assert "# Conversation Brief" in md
    assert "Company 360" in md
    assert "JPMorgan Chase" in md
    assert "Action Plan" in md
    assert "Table of Contents" in md
    assert "Brief Readiness" in md
    assert "Disclaimer" in md


def test_score_brief_completeness():
    data = load_all()
    brief = generate_conversation_brief("C001", "J0001", data["jobs"], "hiring manager", "hiring manager screen")
    result = score_brief_completeness(brief)
    assert 0 <= result["score"] <= 100
    assert result["label"] in ("Ready", "Needs work", "Incomplete")
    assert isinstance(result["gaps"], list)
    assert result["score"] >= 80


def test_conversation_script_no_fake_names():
    script = generate_conversation_script(
        "JPMorgan Chase", "Cloud Security Analyst", "hiring manager",
        "hiring manager screen", {"business_problem": "cloud security monitoring"}, [],
    )
    assert "JPMorgan Chase" in script
    assert "Cloud Security Analyst" in script


def test_next_action_for_hm_screen():
    actions = generate_next_action("hiring manager", "hiring manager screen", [], [])
    assert any("demo" in a.lower() or "30/60/90" in a for a in actions)


def test_role_reasoning_coverage():
    """Every loaded job should have a seeded role_reasoning row."""
    data = load_all()
    jobs = data["jobs"]
    reasoning = data["role_reasoning"]
    assert len(reasoning) >= len(jobs) - 1, (
        f"Expected at least {len(jobs)} role_reasoning rows, got {len(reasoning)}"
    )
    job_ids = set(jobs["job_id"])
    reasoning_ids = set(reasoning["job_id"])
    missing = job_ids - reasoning_ids
    assert not missing, f"Missing role_reasoning for: {sorted(missing)[:5]}"
    assert all(reasoning["why_role_exists"].notna())
    assert all(reasoning["business_problem"].notna())
