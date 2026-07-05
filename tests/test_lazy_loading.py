"""Tests for lazy data loading split in data_loader."""

import pandas as pd

from src.data_loader import load_all, load_core, load_icc_files, load_intelligence, load_mission_control_data


def test_load_core_has_required_keys():
    core = load_core()
    for key in ("companies", "jobs", "contacts", "profile_keywords", "gap_matrix"):
        assert key in core
        assert isinstance(core[key], pd.DataFrame)


def test_load_core_excludes_icc_by_default():
    core = load_core()
    assert "company_profiles" not in core
    assert "people_map" not in core


def test_load_intelligence_scopes_to_company():
    core = load_core()
    company_id = core["companies"].iloc[0]["company_id"]
    intel = load_intelligence(company_id, jobs_df=core["jobs"])
    assert "company_profiles" in intel
    if not intel["company_profiles"].empty:
        assert (intel["company_profiles"]["company_id"] == company_id).all()
    if not intel["people_map"].empty:
        assert (intel["people_map"]["company_id"] == company_id).all()


def test_load_mission_control_data_merges():
    core = load_core()
    icc = load_icc_files()
    merged = load_mission_control_data(core, icc)
    assert "companies" in merged
    assert "company_profiles" in merged
    assert len(merged["company_profiles"]) == len(icc["company_profiles"])


def test_load_all_backward_compatible():
    full = load_all()
    core = load_core()
    assert len(full["companies"]) == len(core["companies"])
    assert "proof_assets" in full
