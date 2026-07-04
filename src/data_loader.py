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


def load_all(data_dir: Path | None = None, validate: bool = True) -> dict[str, pd.DataFrame]:
    """Load, validate, clean, and enrich all datasets."""
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
