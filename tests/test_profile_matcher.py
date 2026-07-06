"""Tests for profile_matcher — job-to-profile scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.profile_matcher import explain_match, match_job_to_profile

SAMPLE_PROFILE = {
    "name": "Test User",
    "headline": "Technology Analyst",
    "target_roles": ["Technology Analyst", "Cloud Security Analyst"],
    "target_locations": ["Plano", "Dallas"],
    "skills": {
        "technical": ["Python", "SQL"],
        "tools": ["AWS"],
        "domains": ["Cloud Security", "Data Analytics"],
    },
    "projects": [
        {"name": "Secure Cloud Lab", "description": "IAM and SIEM analysis", "skills": ["AWS", "SIEM"]},
    ],
    "experience_bullets": ["Built Python automation for cloud security evidence."],
}


def test_match_job_strong_fit():
    job = {
        "job_title": "Technology Analyst",
        "title": "Technology Analyst",
        "description": "Python SQL AWS cloud security data analytics automation in Plano",
        "location": "Plano, TX",
        "role_family": "Technology Analyst / Cloud Security",
    }
    result = match_job_to_profile(job, SAMPLE_PROFILE)
    assert 0 <= result["score"] <= 100
    assert result["fit_tier"] in ("A", "B", "C", "D")
    assert "Python" in result["matched_skills"]
    assert result["tier_reason"]


def test_match_job_weak_fit():
    job = {
        "job_title": "Sales Representative",
        "description": "B2B sales quota hunting cold calling",
        "location": "New York, NY",
        "role_family": "Sales",
    }
    result = match_job_to_profile(job, SAMPLE_PROFILE)
    assert result["score"] < 50
    assert result["fit_tier"] in ("C", "D")


def test_explain_match_readable():
    job = {
        "job_title": "Data Analyst",
        "description": "Python SQL analytics dashboard Tableau",
        "location": "Dallas, TX",
        "role_family": "Data Analyst",
    }
    text = explain_match(job, SAMPLE_PROFILE)
    assert "Data Analyst" in text
    assert "Tier" in text
    assert "Recommendation" in text


def test_match_empty_profile():
    job = {
        "job_title": "Analyst",
        "description": "Python SQL",
        "location": "Plano",
    }
    empty = {"name": "[YOUR NAME]", "skills": {"technical": [], "tools": [], "domains": []}, "target_roles": []}
    result = match_job_to_profile(job, empty)
    assert result["score"] >= 0
    assert "Profile incomplete" in result["tier_reason"] or result["score"] < 40
