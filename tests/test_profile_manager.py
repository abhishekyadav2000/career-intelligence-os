"""Tests for profile_manager — load, save, portfolio summary."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.profile_manager import (
    build_sixty_second_pitch,
    get_portfolio_summary,
    get_profile_for_simulator,
    load_profile,
    save_profile,
)


@pytest.fixture
def tmp_profile(tmp_path):
    path = tmp_path / "user_profile.yaml"
    return path


def test_load_profile_defaults(tmp_profile):
    save_profile({"name": "Test User", "headline": "Analyst"}, tmp_profile)
    profile = load_profile(tmp_profile)
    assert profile["name"] == "Test User"
    assert profile["headline"] == "Analyst"
    assert isinstance(profile["skills"], list)
    assert len(profile["star_stories"]) >= 1


def test_save_and_reload(tmp_profile):
    profile = load_profile(tmp_profile)
    profile["name"] = "Updated Name"
    save_profile(profile, tmp_profile)
    reloaded = load_profile(tmp_profile)
    assert reloaded["name"] == "Updated Name"


def test_get_profile_for_simulator(tmp_profile):
    profile = load_profile(tmp_profile)
    sim = get_profile_for_simulator(profile)
    assert "headline" in sim
    assert "star_stories" in sim
    assert "proof_asset_ids" in sim


def test_build_sixty_second_pitch(tmp_profile):
    profile = load_profile(tmp_profile)
    pitch = build_sixty_second_pitch(profile)
    assert profile["name"] in pitch
    assert profile["headline"] in pitch


def test_get_portfolio_summary(tmp_profile):
    profile = load_profile(tmp_profile)
    summary = get_portfolio_summary(profile=profile)
    assert "proof_assets" in summary
    assert "sixty_second_pitch" in summary
    assert summary["sixty_second_pitch"]
