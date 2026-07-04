#!/usr/bin/env python3
"""
Comprehensive tab and import test for Career Intelligence OS.

Tests:
  - All src module imports (core + backward-compat wrappers)
  - CSV loading via data_loader.load_all()
  - Key engine functions for each dashboard tab (no Streamlit)
  - ICC brief generation for JPMorgan Chase
  - System health check

Usage:
  python scripts/test_all_tabs.py
  python scripts/test_all_tabs.py --verbose
"""

from __future__ import annotations

import argparse
import importlib
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CORE_MODULES = [
    "src.company_priority_scorer",
    "src.company_profile_engine",
    "src.conversation_brief_generator",
    "src.conversation_feedback_analyzer",
    "src.data_loader",
    "src.data_cleaner",
    "src.db",
    "src.health_check",
    "src.interview_topic_mapper",
    "src.keyword_extractor",
    "src.noise_detector",
    "src.outreach_angle_generator",
    "src.people_power_mapper",
    "src.profile_gap_analyzer",
    "src.proof_asset_mapper",
    "src.recommendation_engine",
    "src.research_prompt_generator",
    "src.role_fit_scorer",
    "src.role_reasoning_engine",
    "src.schema_validator",
    "src.sponsorship_signal",
]

COMPAT_MODULES = [
    "src.loader",
    "src.scoring",
    "src.keywords",
    "src.outreach",
    "src.interview",
]

TAB_TESTS = [
    "Interview Command Center",
    "Company 360",
    "People Map",
    "Role Deep Dive",
    "Proof Assets",
    "Overview",
    "Company Ranking",
    "Role Fit",
    "Sponsorship Signal",
    "Networking Map",
    "Interview Prep",
    "Recommendations",
    "Export",
    "Conversation Feedback",
]


class TestReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.passed: list[str] = []

    def ok(self, msg: str) -> None:
        self.passed.append(msg)

    def fail(self, msg: str, exc: Exception | None = None) -> None:
        detail = msg
        if exc:
            tb = traceback.format_exc()
            detail = f"{msg}\n  {type(exc).__name__}: {exc}\n  {tb.strip()}"
        self.errors.append(detail)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def test_imports(report: TestReport, verbose: bool) -> None:
    for mod in CORE_MODULES + COMPAT_MODULES:
        try:
            importlib.import_module(mod)
            report.ok(f"import:{mod}")
            if verbose:
                print(f"  OK  {mod}")
        except Exception as exc:
            report.fail(f"import:{mod}", exc)
            if verbose:
                print(f"  FAIL {mod}: {exc}")


def test_data_load(report: TestReport) -> dict:
    from src.data_loader import load_all

    data = load_all()
    for key in ("companies", "jobs", "contacts", "company_profiles", "people_map", "proof_assets"):
        if key not in data:
            report.fail(f"data_load: missing key '{key}'")
        elif data[key].empty and key not in ("gap_matrix", "conversation_briefs"):
            report.fail(f"data_load: '{key}' is empty")
        else:
            report.ok(f"data_load:{key} ({len(data[key])} rows)")
    return data


def test_tabs(report: TestReport, data: dict) -> None:
    import pandas as pd

    from src.company_priority_scorer import score_companies
    from src.company_profile_engine import build_company_360, get_company_research_gaps, load_company_profiles
    from src.conversation_brief_generator import (
        export_brief_markdown,
        generate_conversation_brief,
        score_brief_completeness,
    )
    from src.conversation_feedback_analyzer import get_dashboard_stats
    from src.db import DEMO_QUERIES, init_db, run_query
    from src.interview_topic_mapper import generate_interview_batch
    from src.outreach_angle_generator import generate_outreach_batch
    from src.people_power_mapper import build_people_map, rank_contacts_for_conversation, load_people_map
    from src.profile_gap_analyzer import analyze_jobs_batch
    from src.proof_asset_mapper import (
        get_top_proof_assets_for_display,
        identify_missing_proof,
        load_proof_assets,
        match_assets_to_company,
        match_assets_to_role,
    )
    from src.recommendation_engine import recommend_batch
    from src.research_prompt_generator import (
        generate_company_research_prompt,
        generate_interview_packet_prompt,
        generate_people_research_prompt,
        generate_role_research_prompt,
    )
    from src.role_fit_scorer import score_jobs_dataframe
    from src.role_reasoning_engine import build_role_deep_dive, load_role_reasoning

    jobs_df = data["jobs"]
    companies_df = data["companies"]
    contacts_df = data["contacts"]
    profiles_df = data.get("company_profiles", load_company_profiles())
    people_df = data.get("people_map", load_people_map())
    proof_df = data.get("proof_assets", load_proof_assets())
    reasoning_df = data.get("role_reasoning", load_role_reasoning())
    projects_df = data.get("company_projects", pd.DataFrame())
    sources_df = data.get("research_sources", pd.DataFrame())

    jpm = companies_df[companies_df["company_name"] == "JPMorgan Chase"]
    if jpm.empty:
        report.fail("tab: JPMorgan Chase not in companies")
        company_id = companies_df.iloc[0]["company_id"]
    else:
        company_id = jpm.iloc[0]["company_id"]

    jpm_jobs = jobs_df[jobs_df["company_name"] == "JPMorgan Chase"]
    job_id = jpm_jobs.iloc[0]["job_id"] if not jpm_jobs.empty else jobs_df.iloc[0]["job_id"]

    scores = score_jobs_dataframe(jobs_df, companies_df)
    company_scores = score_companies(companies_df, jobs_df, contacts_df)
    recommendations = recommend_batch(scores, company_scores)
    outreach = generate_outreach_batch(jobs_df, contacts_df, scores)
    interviews = generate_interview_batch(jobs_df, scores)
    gaps = analyze_jobs_batch(jobs_df, scores)
    init_db(companies_df, jobs_df, contacts_df)

    tab_ops = {
        "Interview Command Center": lambda: (
            generate_conversation_brief(company_id, job_id, jobs_df, "hiring manager", "hiring manager screen"),
            export_brief_markdown(
                generate_conversation_brief(company_id, job_id, jobs_df, "hiring manager", "hiring manager screen")
            ),
            score_brief_completeness(
                generate_conversation_brief(company_id, job_id, jobs_df, "hiring manager", "hiring manager screen")
            ),
        ),
        "Company 360": lambda: (
            build_company_360(company_id, profiles_df, projects_df, sources_df, people_df),
            get_company_research_gaps(company_id, profiles_df, people_df, sources_df),
            generate_company_research_prompt(company_id),
        ),
        "People Map": lambda: (
            build_people_map(company_id, people_df),
            rank_contacts_for_conversation(company_id, "hiring manager", "hiring manager screen", people_df),
            generate_people_research_prompt(company_id),
        ),
        "Role Deep Dive": lambda: (
            build_role_deep_dive(job_id, jobs_df, reasoning_df),
            generate_role_research_prompt(job_id, jobs_df),
        ),
        "Proof Assets": lambda: (
            get_top_proof_assets_for_display(job_id, company_id, proof_df, jobs_df, profiles_df, n=3),
            identify_missing_proof(job_id, company_id, proof_df, jobs_df, profiles_df),
            match_assets_to_company(company_id, proof_df, profiles_df),
            match_assets_to_role(job_id, proof_df, jobs_df),
            generate_interview_packet_prompt(company_id, job_id, jobs_df, "hiring manager"),
        ),
        "Overview": lambda: (len(companies_df), len(jobs_df), len(contacts_df), gaps),
        "Company Ranking": lambda: company_scores,
        "Role Fit": lambda: scores,
        "Sponsorship Signal": lambda: [s.get("sponsorship_detail", {}) for s in scores[:3]],
        "Networking Map": lambda: outreach[:5],
        "Interview Prep": lambda: interviews[:3],
        "Recommendations": lambda: recommendations[:5],
        "Export": lambda: (run_query(DEMO_QUERIES[list(DEMO_QUERIES.keys())[0]]),),
        "Conversation Feedback": lambda: get_dashboard_stats(),
    }

    for tab_name in TAB_TESTS:
        try:
            tab_ops[tab_name]()
            report.ok(f"tab:{tab_name}")
        except Exception as exc:
            report.fail(f"tab:{tab_name}", exc)


def test_health_check(report: TestReport) -> None:
    from src.health_check import run_health_check

    result = run_health_check()
    if result["overall"] == "red":
        report.fail(f"health_check: overall status red")
    else:
        report.ok(f"health_check:{result['overall']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Test all Career Intelligence OS tabs and imports")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    report = TestReport()

    print("=" * 60)
    print("Career Intelligence OS — Full Tab & Import Test")
    print("=" * 60)

    print("\n[1/4] Module imports...")
    test_imports(report, args.verbose)

    print("\n[2/4] Data loading...")
    try:
        data = test_data_load(report)
    except Exception as exc:
        report.fail("data_load:load_all", exc)
        data = {}

    if data:
        print("\n[3/4] Tab simulations (14 tabs)...")
        test_tabs(report, data)

    print("\n[4/4] Health check...")
    test_health_check(report)

    print("\n" + "=" * 60)
    print(f"PASSED: {len(report.passed)}")
    print(f"FAILED: {len(report.errors)}")
    print("=" * 60)

    if report.errors:
        print("\nERRORS:")
        for err in report.errors:
            print(f"\n---\n{err}")
        return 1

    print("\nAll tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
