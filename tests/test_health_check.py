"""Tests for system health check."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.health_check import check_csvs, check_imports, check_pipeline, run_health_check


def test_check_imports_all_green():
    result = check_imports()
    assert result["status"] == "green"
    assert all(c["status"] == "green" for c in result["checks"])


def test_check_csvs_required_present():
    result = check_csvs()
    assert result["status"] == "green"
    required = [c for c in result["checks"] if c["file"] in (
        "sample_companies.csv", "sample_jobs.csv", "sample_contacts.csv",
        "company_profiles.csv", "people_map.csv", "proof_assets.csv",
    )]
    assert all(c["rows"] > 0 for c in required)


def test_check_pipeline_runs():
    result = check_pipeline()
    assert result["status"] == "green"
    assert any(c["step"] == "icc_brief" for c in result["checks"])


def test_run_health_check_overall():
    result = run_health_check()
    assert result["overall"] in ("green", "yellow")
    assert "imports" in result
    assert "csvs" in result
    assert "pipeline" in result
