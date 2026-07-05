"""Load and validate CSV datasets with schema enforcement."""

from pathlib import Path

import pandas as pd

from src.data_cleaner import clean_all
from src.schema_validator import validate_all

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FILE_MAP = {
    "companies": "sample_companies.csv",
    "jobs": "sample_jobs.csv",
    "contacts": "sample_contacts.csv",
    "profile_keywords": "profile_keywords.csv",
}

INTERVIEW_COMMAND_CENTER_FILES = {
    "company_profiles": "company_profiles.csv",
    "people_map": "people_map.csv",
    "company_projects": "company_projects.csv",
    "role_reasoning": "role_reasoning.csv",
    "proof_assets": "proof_assets.csv",
    "conversation_briefs": "conversation_briefs.csv",
    "research_sources": "research_sources.csv",
    "interview_insights": "interview_insights.csv",
    "interview_journey": "interview_journey.csv",
}


def _add_ids(companies: pd.DataFrame, jobs: pd.DataFrame, contacts: pd.DataFrame):
    """Add stable IDs and legacy column aliases for downstream modules."""
    company_ids = {name: f"C{i:03d}" for i, name in enumerate(companies["company"].unique(), 1)}
    companies = companies.copy()
    companies["company_id"] = companies["company"].map(company_ids)
    companies["company_name"] = companies["company"]
    companies["priority_tier"] = companies["notes"].str.extract(r"(Tier \d[^;]*)")[0].fillna("Tier 2")
    companies["h1b_confidence"] = companies["sponsor_signal"].str.lower().str.count(r"sponsor|h1b|campus|mega").clip(0, 5)
    companies["dfw_fit"] = companies["location"].str.contains("Dallas|Plano|Irving|DFW|Fort Worth", case=False, na=False).astype(int) * 5
    companies["role_fit"] = 4
    companies["rank"] = range(1, len(companies) + 1)

    jobs = jobs.copy()
    jobs["company_id"] = jobs["company"].map(company_ids)
    jobs["company_name"] = jobs["company"]
    jobs["job_id"] = [f"J{i:04d}" for i in range(1, len(jobs) + 1)]
    jobs["role_cluster"] = jobs["role_family"]
    jobs["business_problem"] = jobs["visa_notes"].str.split("—").str[0].str.strip()
    jobs["priority_tier"] = jobs["company"].map(
        dict(zip(companies["company"], companies["notes"].str.extract(r"(Tier \d[^;]*)")[0].fillna("Tier 2")))
    )
    jobs["status"] = "open"

    contacts = contacts.copy()
    contacts["company_id"] = contacts["company"].map(company_ids)
    contacts["company_name"] = contacts["company"]
    contacts["contact_id"] = [f"CT{i:04d}" for i in range(1, len(contacts) + 1)]
    contacts["name"] = contacts["search_query"]
    contacts["persona"] = contacts["search_query"]
    contacts["linkedin_search"] = contacts["LinkedIn_search_url"]
    contacts["status"] = contacts["notes"].str.extract(r"Status:\s*(\w+)")[0].fillna("not_contacted")

    return companies, jobs, contacts


def load_raw(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load CSV files without cleaning."""
    base = data_dir or DATA_DIR
    return {key: pd.read_csv(base / fname) for key, fname in FILE_MAP.items()}


def _load_icc_files(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load Interview Command Center CSV files (unfiltered)."""
    base = data_dir or DATA_DIR
    icc_data: dict[str, pd.DataFrame] = {}
    for key, fname in INTERVIEW_COMMAND_CENTER_FILES.items():
        fpath = base / fname
        icc_data[key] = pd.read_csv(fpath) if fpath.exists() else pd.DataFrame()
    return icc_data


def load_icc_files(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load all Interview Command Center CSV files (public alias)."""
    return _load_icc_files(data_dir)


def load_core(data_dir: Path | None = None, validate: bool = True) -> dict[str, pd.DataFrame]:
    """Load core datasets only — companies, jobs, contacts, keywords, gap matrix."""
    raw = load_raw(data_dir)
    if validate:
        reports = validate_all(raw)
        invalid = [r for r in reports if not r.valid]
        if invalid:
            msgs = [f"{r.dataset}: missing={r.missing_columns}, empty={r.empty_rows}" for r in invalid]
            raise ValueError(f"Schema validation failed: {'; '.join(msgs)}")

    cleaned = clean_all(raw)
    companies, jobs, contacts = _add_ids(cleaned["companies"], cleaned["jobs"], cleaned["contacts"])

    gap_path = (data_dir or DATA_DIR) / "gap_matrix.csv"
    gap_matrix = pd.read_csv(gap_path) if gap_path.exists() else pd.DataFrame()

    return {
        "companies": companies,
        "jobs": jobs,
        "contacts": contacts,
        "profile_keywords": cleaned["profile_keywords"],
        "gap_matrix": gap_matrix,
    }


def load_intelligence(company_id: str, data_dir: Path | None = None, jobs_df: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    """Load ICC datasets scoped to one company — avoids loading all 50 company profiles on every render."""
    icc = _load_icc_files(data_dir)
    cid = company_id or ""

    def _filter_col(df: pd.DataFrame, col: str = "company_id") -> pd.DataFrame:
        if df.empty or not cid or col not in df.columns:
            return df
        return df[df[col] == cid].copy()

    company_profiles = _filter_col(icc.get("company_profiles", pd.DataFrame()))
    people_map = _filter_col(icc.get("people_map", pd.DataFrame()))
    company_projects = _filter_col(icc.get("company_projects", pd.DataFrame()))
    research_sources = _filter_col(icc.get("research_sources", pd.DataFrame()))
    interview_insights = _filter_col(icc.get("interview_insights", pd.DataFrame()))
    interview_journey = _filter_col(icc.get("interview_journey", pd.DataFrame()))

    role_reasoning = icc.get("role_reasoning", pd.DataFrame())
    if not role_reasoning.empty and jobs_df is not None and not jobs_df.empty and cid:
        job_ids = jobs_df[jobs_df["company_id"] == cid]["job_id"].tolist()
        if job_ids and "job_id" in role_reasoning.columns:
            role_reasoning = role_reasoning[role_reasoning["job_id"].isin(job_ids)].copy()

    return {
        "company_profiles": company_profiles,
        "people_map": people_map,
        "company_projects": company_projects,
        "research_sources": research_sources,
        "role_reasoning": role_reasoning,
        "proof_assets": icc.get("proof_assets", pd.DataFrame()),
        "conversation_briefs": icc.get("conversation_briefs", pd.DataFrame()),
        "interview_insights": interview_insights,
        "interview_journey": interview_journey,
    }


def load_mission_control_data(
    core: dict[str, pd.DataFrame],
    intelligence: dict[str, pd.DataFrame] | None = None,
) -> dict[str, pd.DataFrame]:
    """Merge core + intelligence into a single dict for mission_control_engine."""
    merged = dict(core)
    if intelligence:
        merged.update(intelligence)
    else:
        merged.update(_load_icc_files())
    return merged


def load_all(data_dir: Path | None = None, validate: bool = True) -> dict[str, pd.DataFrame]:
    """Load, validate, clean, and enrich all datasets."""
    core = load_core(data_dir, validate=validate)
    icc = _load_icc_files(data_dir)
    return {**core, **icc}
