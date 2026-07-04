"""System health check — validates imports, CSV datasets, and module readiness."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

CORE_MODULES = [
    "src.company_priority_scorer",
    "src.company_profile_engine",
    "src.conversation_brief_generator",
    "src.conversation_feedback_analyzer",
    "src.data_loader",
    "src.data_cleaner",
    "src.db",
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
    "src.mission_control_engine",
    "src.message_queue_engine",
    "src.pipeline_engine",
    "src.schedule_engine",
    "src.data_confidence",
]

COMPAT_MODULES = [
    "src.loader",
    "src.scoring",
    "src.keywords",
    "src.outreach",
    "src.interview",
]

REQUIRED_CSVS = [
    "sample_companies.csv",
    "sample_jobs.csv",
    "sample_contacts.csv",
    "profile_keywords.csv",
    "company_profiles.csv",
    "people_map.csv",
    "company_projects.csv",
    "role_reasoning.csv",
    "proof_assets.csv",
    "research_sources.csv",
]

OPTIONAL_CSVS = [
    "gap_matrix.csv",
    "conversation_briefs.csv",
    "pipeline_cards.csv",
    "monday_launch_plan.csv",
    "activity_schedule.csv",
    "sample_conversation_log.csv",
]


def _status_from_checks(checks: list[bool]) -> str:
    if not checks:
        return "yellow"
    if all(checks):
        return "green"
    if any(checks):
        return "yellow"
    return "red"


def check_imports() -> dict[str, Any]:
    """Verify all src modules import without error."""
    results: list[dict[str, str]] = []
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    for mod_name in CORE_MODULES + COMPAT_MODULES:
        try:
            importlib.import_module(mod_name)
            results.append({"module": mod_name, "status": "green", "detail": "OK"})
        except Exception as exc:
            results.append({
                "module": mod_name,
                "status": "red",
                "detail": f"{type(exc).__name__}: {exc}",
            })

    statuses = [r["status"] for r in results]
    overall = "green" if all(s == "green" for s in statuses) else (
        "red" if any(s == "red" for s in statuses) else "yellow"
    )
    return {"status": overall, "checks": results}


def check_csvs(data_dir: Path | None = None) -> dict[str, Any]:
    """Validate CSV presence and row counts."""
    base = data_dir or (ROOT / "data")
    results: list[dict[str, Any]] = []

    for fname in REQUIRED_CSVS:
        path = base / fname
        if not path.exists():
            results.append({"file": fname, "status": "red", "rows": 0, "detail": "Missing"})
            continue
        try:
            import pandas as pd

            df = pd.read_csv(path)
            status = "green" if len(df) > 0 else "yellow"
            results.append({"file": fname, "status": status, "rows": len(df), "detail": "OK"})
        except Exception as exc:
            results.append({
                "file": fname,
                "status": "red",
                "rows": 0,
                "detail": f"{type(exc).__name__}: {exc}",
            })

    for fname in OPTIONAL_CSVS:
        path = base / fname
        if not path.exists():
            results.append({"file": fname, "status": "yellow", "rows": 0, "detail": "Optional — not present"})
            continue
        try:
            import pandas as pd

            df = pd.read_csv(path)
            results.append({"file": fname, "status": "green", "rows": len(df), "detail": "OK"})
        except Exception as exc:
            results.append({
                "file": fname,
                "status": "red",
                "rows": 0,
                "detail": f"{type(exc).__name__}: {exc}",
            })

    statuses = [r["status"] for r in results if r["file"] in REQUIRED_CSVS]
    overall = _status_from_checks([s == "green" for s in statuses])
    if any(r["status"] == "red" for r in results):
        overall = "red"
    return {"status": overall, "checks": results}


def check_pipeline() -> dict[str, Any]:
    """Run load_all and key engine functions without Streamlit."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    steps: list[dict[str, str]] = []
    try:
        from src.data_loader import load_all
        from src.role_fit_scorer import score_jobs_dataframe
        from src.company_priority_scorer import score_companies
        from src.recommendation_engine import recommend_batch
        from src.conversation_brief_generator import generate_conversation_brief

        data = load_all()
        steps.append({"step": "load_all", "status": "green", "detail": f"{len(data['jobs'])} jobs"})

        scores = score_jobs_dataframe(data["jobs"], data["companies"])
        steps.append({"step": "score_jobs", "status": "green", "detail": f"{len(scores)} scored"})

        company_scores = score_companies(data["companies"], data["jobs"], data["contacts"])
        steps.append({"step": "score_companies", "status": "green", "detail": f"{len(company_scores)} ranked"})

        recs = recommend_batch(scores, company_scores)
        steps.append({"step": "recommendations", "status": "green", "detail": f"{len(recs)} actions"})

        jpm = data["companies"][data["companies"]["company_name"] == "JPMorgan Chase"]
        company_id = jpm.iloc[0]["company_id"] if not jpm.empty else data["companies"].iloc[0]["company_id"]
        job_id = data["jobs"].iloc[0]["job_id"]
        brief = generate_conversation_brief(
            company_id, job_id, data["jobs"], "hiring manager", "hiring manager screen",
        )
        steps.append({"step": "icc_brief", "status": "green", "detail": brief["brief_id"]})

        overall = "green"
    except Exception as exc:
        steps.append({"step": "pipeline", "status": "red", "detail": f"{type(exc).__name__}: {exc}"})
        overall = "red"

    return {"status": overall, "checks": steps}


def run_health_check(data_dir: Path | None = None) -> dict[str, Any]:
    """Run full system health check."""
    imports = check_imports()
    csvs = check_csvs(data_dir)
    pipeline = check_pipeline()

    statuses = [imports["status"], csvs["status"], pipeline["status"]]
    if "red" in statuses:
        overall = "red"
    elif "yellow" in statuses:
        overall = "yellow"
    else:
        overall = "green"

    return {
        "overall": overall,
        "imports": imports,
        "csvs": csvs,
        "pipeline": pipeline,
    }
