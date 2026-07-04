"""Ensure people_map has no TBD or placeholder demo rows."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_all


def test_no_placeholder_verification_status():
    data = load_all()
    people = data["people_map"]
    placeholders = people[people["verification_status"].str.lower() == "placeholder"]
    assert placeholders.empty, f"Found {len(placeholders)} placeholder rows in people_map"


def test_no_tbd_person_names():
    data = load_all()
    people = data["people_map"]
    tbd = people[people["person_name"].str.contains("TBD", case=False, na=False)]
    assert tbd.empty, f"Found {len(tbd)} rows with TBD in person_name"


def test_all_companies_have_profiles():
    data = load_all()
    companies = data["companies"]
    profiles = data["company_profiles"]
    assert len(profiles) == len(companies), (
        f"Expected {len(companies)} profiles, got {len(profiles)}"
    )


def test_all_companies_have_research_sources():
    data = load_all()
    companies = set(data["companies"]["company_id"])
    sources = data["research_sources"]
    covered = set(sources["company_id"].unique())
    missing = companies - covered
    assert not missing, f"Missing research_sources for: {sorted(missing)[:5]}"


def test_profiles_last_updated_fresh():
    data = load_all()
    profiles = data["company_profiles"]
    assert all(profiles["last_updated"] >= "2026-07-04")
