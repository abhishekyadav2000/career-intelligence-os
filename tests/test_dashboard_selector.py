"""Tests for dashboard global selector state and company coverage."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard.icc_state import (
    build_company_options,
    format_company_option,
    get_jobs_for_company,
    init_icc_state,
    on_company_change,
    on_job_change,
    resolve_icc_context,
    set_target,
)
from src.company_priority_scorer import score_companies
from src.data_loader import load_all


class SessionStub(dict):
    """Minimal session_state stand-in for unit tests."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


@pytest.fixture
def pipeline_data():
    data = load_all()
    company_scores = score_companies(data["companies"], data["jobs"], data["contacts"])
    company_rank_df = __import__("pandas").DataFrame(company_scores)
    return data, company_rank_df


def test_company_dropdown_includes_all_fifty_companies(pipeline_data):
    data, company_rank_df = pipeline_data
    companies_df = data["companies"]
    options = build_company_options(companies_df, company_rank_df)
    assert len(companies_df) == 50
    assert len(options) == 50
    assert len(set(options)) == 50


def test_company_search_filters_without_dropping_total_pool(pipeline_data):
    data, company_rank_df = pipeline_data
    companies_df = data["companies"]
    all_options = build_company_options(companies_df, company_rank_df)
    filtered = build_company_options(companies_df, company_rank_df, search="jpmorgan")
    assert len(filtered) == 1
    assert format_company_option(filtered[0], companies_df).startswith("JPMorgan Chase")
    assert len(all_options) == 50


def test_session_state_sync_on_company_change(pipeline_data):
    data, _ = pipeline_data
    companies_df = data["companies"]
    jobs_df = data["jobs"]
    session = SessionStub()
    init_icc_state(session, companies_df, jobs_df)

    dell = companies_df[companies_df["company_name"].str.contains("Dell", case=False, na=False)].iloc[0]
    session.icc_company_id = dell["company_id"]
    on_company_change(session, companies_df, jobs_df)

    assert session.icc_company_name == dell["company_name"]
    assert session.icc_job_id
    job_row = jobs_df[jobs_df["job_id"] == session.icc_job_id].iloc[0]
    assert job_row["company_id"] == dell["company_id"]
    assert session.icc_job_title == job_row["title"]


def test_session_state_sync_on_job_change(pipeline_data):
    data, _ = pipeline_data
    companies_df = data["companies"]
    jobs_df = data["jobs"]
    session = SessionStub()
    init_icc_state(session, companies_df, jobs_df)

    jpm_jobs = get_jobs_for_company("C001", jobs_df)
    second_job = jpm_jobs.iloc[1]["job_id"]
    session.icc_job_id = second_job
    on_job_change(session, jobs_df)

    assert session.icc_company_id == "C001"
    assert session.icc_job_title == jpm_jobs.iloc[1]["title"]


def test_set_target_from_mission_control(pipeline_data):
    data, _ = pipeline_data
    companies_df = data["companies"]
    jobs_df = data["jobs"]
    session = SessionStub()
    init_icc_state(session, companies_df, jobs_df)

    target_job = jobs_df[jobs_df["company_id"] == "C004"].iloc[0]
    set_target(session, "C004", target_job["job_id"], companies_df, jobs_df)
    ctx = resolve_icc_context(session, companies_df, jobs_df)

    assert ctx["company_id"] == "C004"
    assert ctx["company_name"] == "Citi"
    assert ctx["job_id"] == target_job["job_id"]
    assert ctx["selection_complete"] is True


def test_resolve_icc_context_migrates_legacy_keys(pipeline_data):
    data, _ = pipeline_data
    companies_df = data["companies"]
    jobs_df = data["jobs"]
    session = SessionStub({
        "icc_company": "Capital One",
        "icc_job": jobs_df[jobs_df["company_name"] == "Capital One"].iloc[0]["job_id"],
        "icc_conv_type": "recruiter",
        "icc_stage": "recruiter screen",
    })
    ctx = resolve_icc_context(session, companies_df, jobs_df)
    assert ctx["company_name"] == "Capital One"
    assert ctx["person_type"] == "recruiter"
    assert ctx["interview_stage"] == "recruiter screen"
