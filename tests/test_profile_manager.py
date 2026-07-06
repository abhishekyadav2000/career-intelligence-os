"""Tests for profile_manager — load, save, validation, completeness."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.profile_manager import (
    build_positioning_statement,
    build_sixty_second_pitch,
    get_portfolio_summary,
    get_profile_for_simulator,
    get_skills_for_matching,
    get_target_role_families,
    load_profile,
    profile_completeness_score,
    save_profile,
    validate_profile,
)

SAMPLE_PROFILE = {
    "name": "Test User",
    "headline": "Technology Analyst",
    "positioning": "I build data and automation systems.",
    "location": "DFW / Plano",
    "authorization": "OPT/EAD",
    "target_roles": ["Technology Analyst", "Data Analyst"],
    "target_industries": ["Financial Services"],
    "target_locations": ["Plano", "Dallas"],
    "years_experience": 2,
    "education": {
        "school": "Test University",
        "degree": "MS Information Systems",
        "graduation": "2026",
        "relevant_coursework": ["Database Systems"],
    },
    "skills": {
        "technical": ["Python", "SQL"],
        "tools": ["AWS", "Tableau"],
        "domains": ["Cloud Security"],
    },
    "experience_bullets": ["Built a scoring dashboard with Python and Streamlit."],
    "projects": [
        {"name": "CI OS", "description": "Role-fit dashboard", "skills": ["Python"], "url": ""},
    ],
    "star_stories": [
        {
            "id": "STAR001",
            "title": "Dashboard",
            "situation": "Need unified view",
            "task": "Build dashboard",
            "action": "Used Python",
            "result": "Shipped demo",
            "tags": ["python"],
        }
    ],
    "career_goals": "Analyst role in DFW",
    "networking_positioning": "Builder, not generic job seeker",
    "proof_asset_ids": ["PA001"],
    "portfolio_links": [],
}


@pytest.fixture
def tmp_profile(tmp_path):
    path = tmp_path / "user_profile.yaml"
    return path


def test_load_profile_defaults(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    profile = load_profile(tmp_profile)
    assert profile["name"] == "Test User"
    assert profile["headline"] == "Technology Analyst"
    assert isinstance(profile["skills"], dict)
    assert "technical" in profile["skills"]
    assert len(profile["star_stories"]) >= 1


def test_save_and_reload(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    profile = load_profile(tmp_profile)
    profile["name"] = "Updated Name"
    save_profile(profile, tmp_profile)
    reloaded = load_profile(tmp_profile)
    assert reloaded["name"] == "Updated Name"


def test_get_skills_for_matching(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    skills = get_skills_for_matching(load_profile(tmp_profile))
    assert "Python" in skills
    assert "AWS" in skills
    assert "Cloud Security" in skills


def test_get_target_role_families(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    roles = get_target_role_families(load_profile(tmp_profile))
    assert "Technology Analyst" in roles
    assert "Data Analyst" in roles


def test_validate_profile_valid(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    result = validate_profile(load_profile(tmp_profile))
    assert result["valid"] is True


def test_validate_profile_missing_required(tmp_profile):
    save_profile({"name": "[YOUR NAME]", "headline": "", "positioning": ""}, tmp_profile)
    result = validate_profile(load_profile(tmp_profile))
    assert result["valid"] is False
    assert any("headline" in e for e in result["errors"])


def test_profile_completeness_score(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    result = profile_completeness_score(load_profile(tmp_profile))
    assert 0 <= result["score"] <= 100
    assert result["score"] >= 60
    assert isinstance(result["missing"], list)


def test_profile_completeness_empty(tmp_profile):
    save_profile({"name": "[YOUR NAME]"}, tmp_profile)
    result = profile_completeness_score(load_profile(tmp_profile))
    assert result["score"] < 30
    assert len(result["missing"]) > 5


def test_get_profile_for_simulator(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    sim = get_profile_for_simulator(load_profile(tmp_profile))
    assert "headline" in sim
    assert "star_stories" in sim
    assert "experience_bullets" in sim
    assert "Python" in sim["skills"]


def test_build_positioning_statement(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    stmt = build_positioning_statement(load_profile(tmp_profile))
    assert "Test User" in stmt
    assert "Technology Analyst" in stmt


def test_build_sixty_second_pitch(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    pitch = build_sixty_second_pitch(load_profile(tmp_profile))
    assert "Test User" in pitch


def test_get_portfolio_summary(tmp_profile):
    save_profile(SAMPLE_PROFILE, tmp_profile)
    summary = get_portfolio_summary(profile=load_profile(tmp_profile))
    assert "proof_assets" in summary
    assert "sixty_second_pitch" in summary
    assert "completeness" in summary
    assert summary["sixty_second_pitch"]
