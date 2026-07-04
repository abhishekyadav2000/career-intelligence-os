"""Tests for scoring engine modules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.company_priority_scorer import score_companies
from src.data_loader import load_all
from src.noise_detector import detect_noise
from src.recommendation_engine import recommend
from src.role_fit_scorer import UNIVERSAL_PROFILE, score_role_fit, score_jobs_dataframe
from src.sponsorship_signal import score_sponsorship


def test_universal_profile():
    assert "Enterprise Technology Analyst" in UNIVERSAL_PROFILE


def test_score_role_fit_returns_categories():
    result = score_role_fit(
        description="Python SQL AWS IAM SIEM automation data pipeline analytics risk controls agile",
        title="Cloud Security Analyst",
        location="Plano / Dallas",
        visa_notes="H1B sponsor history — validate via DOL",
    )
    assert 0 <= result["fit_score"] <= 100
    assert "technical_fit" in result["category_scores"]
    assert "sponsorship_signal" in result["category_scores"]
    assert "noise_risk" in result["category_scores"]


def test_sponsorship_disclaimer():
    result = score_sponsorship("validate sponsorship via DOL/USCIS")
    assert "disclaimer" in result
    assert "not legal certainty" in result["disclaimer"].lower()


def test_noise_detector():
    result = detect_noise("Short desc", "Analyst")
    assert "risk_score" in result


def test_recommendation_actions():
    score = {"fit_score": 80, "category_scores": {"noise_risk": 10, "sponsorship_signal": 70, "networking_opportunity": 75}}
    rec = recommend(score, company_priority=85)
    assert rec["action"] in ("apply now", "network first", "research more", "skip/watchlist")


def test_load_and_score_pipeline():
    data = load_all()
    assert len(data["companies"]) >= 45
    assert len(data["jobs"]) >= 100
    scores = score_jobs_dataframe(data["jobs"], data["companies"])
    assert len(scores) == len(data["jobs"])
    company_scores = score_companies(data["companies"], data["jobs"], data["contacts"])
    assert len(company_scores) == len(data["companies"])


if __name__ == "__main__":
    tests = [
        test_universal_profile,
        test_score_role_fit_returns_categories,
        test_sponsorship_disclaimer,
        test_noise_detector,
        test_recommendation_actions,
        test_load_and_score_pipeline,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"PASS: {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL: {t.__name__} — {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
