"""Normalize company names, locations, titles, and role families."""

import re

import pandas as pd

LOCATION_ALIASES = {
    "plano/dallas": "Plano / Dallas",
    "dallas/plano": "Plano / Dallas",
    "dfw": "Dallas-Fort Worth",
    "irving tx": "Irving",
}

ROLE_FAMILY_MAP = {
    "cloud / security / data / ai / analyst": "Enterprise Technology",
    "cloud security": "Cloud Security",
    "data analytics": "Data Analytics",
    "ai automation": "AI Automation",
}


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip()) if pd.notna(text) else ""


def normalize_company_name(name: str) -> str:
    return _normalize_whitespace(name)


def normalize_location(location: str) -> str:
    loc = _normalize_whitespace(location)
    return LOCATION_ALIASES.get(loc.lower(), loc)


def normalize_title(title: str) -> str:
    title = _normalize_whitespace(title)
    return title.title() if title.islower() else title


def normalize_role_family(role_family: str) -> str:
    rf = _normalize_whitespace(role_family)
    return ROLE_FAMILY_MAP.get(rf.lower(), rf)


def clean_companies(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["company"] = out["company"].map(normalize_company_name)
    out["location"] = out["location"].map(normalize_location)
    out["industry"] = out["industry"].map(_normalize_whitespace)
    return out.drop_duplicates(subset=["company"], keep="first")


def clean_jobs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["company"] = out["company"].map(normalize_company_name)
    out["location"] = out["location"].map(normalize_location)
    out["title"] = out["title"].map(normalize_title)
    out["role_family"] = out["role_family"].map(normalize_role_family)
    return out.drop_duplicates(subset=["company", "title"], keep="first")


def clean_contacts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["company"] = out["company"].map(normalize_company_name)
    out["contact_type"] = out["contact_type"].str.lower().str.strip()
    return out.drop_duplicates(subset=["company", "contact_type", "search_query"], keep="first")


def clean_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply cleaners to all datasets."""
    cleaners = {
        "companies": clean_companies,
        "jobs": clean_jobs,
        "contacts": clean_contacts,
    }
    return {k: cleaners[k](v) if k in cleaners else v for k, v in datasets.items()}
