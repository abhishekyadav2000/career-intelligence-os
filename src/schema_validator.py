"""CSV schema validation utilities."""

from dataclasses import dataclass, field

import pandas as pd

SCHEMAS: dict[str, list[str]] = {
    "companies": ["company", "industry", "location", "sponsor_signal", "target_roles", "career_url", "notes"],
    "jobs": ["company", "title", "location", "job_url", "description", "posted_date", "role_family", "visa_notes"],
    "contacts": ["company", "contact_type", "search_query", "LinkedIn_search_url", "message_angle", "notes"],
    "profile_keywords": ["skill", "category", "weight"],
}


@dataclass
class ValidationReport:
    dataset: str
    missing_columns: list[str] = field(default_factory=list)
    empty_rows: int = 0
    duplicate_rows: int = 0
    row_count: int = 0
    valid: bool = True

    def __post_init__(self):
        if self.missing_columns or self.empty_rows or self.duplicate_rows:
            self.valid = False


def validate_schema(df: pd.DataFrame, dataset: str) -> ValidationReport:
    """Check required columns, empty rows, and duplicates."""
    required = SCHEMAS.get(dataset, [])
    missing = [c for c in required if c not in df.columns]
    report = ValidationReport(dataset=dataset, missing_columns=missing, row_count=len(df))

    if missing:
        return report

    key_col = "company" if dataset != "profile_keywords" else "skill"
    if key_col in df.columns:
        report.empty_rows = int(df[key_col].isna().sum() + (df[key_col].astype(str).str.strip() == "").sum())
        subset_map = {
            "profile_keywords": ["skill"],
            "jobs": ["company", "title"],
            "contacts": ["company", "contact_type"],
            "companies": ["company"],
        }
        subset = subset_map.get(dataset, [key_col])
        subset = [c for c in subset if c in df.columns]
        if subset:
            report.duplicate_rows = int(df.duplicated(subset=subset, keep=False).sum())

    return report


def validate_all(datasets: dict[str, pd.DataFrame]) -> list[ValidationReport]:
    """Validate all loaded datasets."""
    return [validate_schema(df, name) for name, df in datasets.items() if name in SCHEMAS]
