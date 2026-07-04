"""CSV data loading utilities."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_companies(data_dir: Path | None = None) -> pd.DataFrame:
    """Load company targeting data from CSV."""
    path = (data_dir or DATA_DIR) / "companies.csv"
    return pd.read_csv(path)


def load_jobs(data_dir: Path | None = None) -> pd.DataFrame:
    """Load job postings from CSV."""
    path = (data_dir or DATA_DIR) / "jobs.csv"
    return pd.read_csv(path)


def load_contacts(data_dir: Path | None = None) -> pd.DataFrame:
    """Load networking contacts from CSV."""
    path = (data_dir or DATA_DIR) / "contacts.csv"
    return pd.read_csv(path)


def load_gap_matrix(data_dir: Path | None = None) -> pd.DataFrame:
    """Load portfolio capability gap matrix from CSV."""
    path = (data_dir or DATA_DIR) / "gap_matrix.csv"
    return pd.read_csv(path)


def load_all(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load all datasets into a dictionary."""
    return {
        "companies": load_companies(data_dir),
        "jobs": load_jobs(data_dir),
        "contacts": load_contacts(data_dir),
        "gap_matrix": load_gap_matrix(data_dir),
    }
