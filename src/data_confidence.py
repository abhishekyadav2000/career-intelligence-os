"""Data confidence labels for CSV-backed intelligence."""

from __future__ import annotations

from datetime import datetime, timedelta

CONFIDENCE_LABELS = (
    "verified_public",
    "user_verified",
    "source_backed",
    "hypothesis",
    "placeholder",
    "stale",
)

VERIFICATION_TO_CONFIDENCE = {
    "verified": "user_verified",
    "verified_public": "verified_public",
    "source_backed": "source_backed",
    "partial": "source_backed",
    "needs_verification": "hypothesis",
    "placeholder": "placeholder",
}


def parse_date(value: str | None) -> datetime | None:
    if not value or str(value).strip() in ("", "TBD", "N/A"):
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(value).strip()[:10], fmt)
        except ValueError:
            continue
    return None


def is_stale(last_updated: str | None, days: int = 30, reference: datetime | None = None) -> bool:
    """Return True if last_updated is older than `days` or unparseable."""
    ref = reference or datetime.now()
    parsed = parse_date(last_updated)
    if parsed is None:
        return True
    return (ref - parsed) > timedelta(days=days)


def compute_confidence(
    verification_status: str = "placeholder",
    last_updated: str | None = None,
    has_sources: bool = False,
    reference: datetime | None = None,
) -> str:
    """Map verification + freshness + sources to a confidence label."""
    if is_stale(last_updated, reference=reference):
        return "stale"
    base = VERIFICATION_TO_CONFIDENCE.get(
        (verification_status or "placeholder").lower().strip(),
        "hypothesis",
    )
    if has_sources and base in ("hypothesis", "placeholder"):
        return "source_backed"
    return base


def confidence_badge_label(confidence: str) -> str:
    return confidence.replace("_", " ").title()


def has_valid_source_url(value: str | None) -> bool:
    """Return True if value looks like a verifiable http(s) URL."""
    if not value or str(value).strip() in ("", "TBD", "N/A", "nan"):
        return False
    text = str(value).strip().lower()
    return text.startswith("http://") or text.startswith("https://")


def flag_missing_source_urls(
    df,
    url_column: str = "source_url",
    id_column: str | None = None,
) -> list[str]:
    """Return warnings for rows missing source_url in a dataframe."""
    warnings: list[str] = []
    if df is None or df.empty or url_column not in df.columns:
        return warnings
    missing = df[~df[url_column].apply(has_valid_source_url)]
    if missing.empty:
        return warnings
    label = id_column if id_column and id_column in missing.columns else url_column
    for _, row in missing.head(10).iterrows():
        ident = row.get(label, "row") if label in row.index else "row"
        warnings.append(f"Missing verified source_url: {ident}")
    extra = len(missing) - min(10, len(missing))
    if extra > 0:
        warnings.append(f"...and {extra} more rows missing source_url")
    return warnings


def validate_dataset_sources(
    profiles_df,
    projects_df,
    insights_df,
) -> dict[str, list[str]]:
    """Validate source_url presence across key intelligence datasets."""
    return {
        "company_profiles": flag_missing_source_urls(profiles_df, "source_urls"),
        "company_projects": flag_missing_source_urls(projects_df, "source_url", "project_id"),
        "interview_insights": flag_missing_source_urls(insights_df, "source_url", "insight_id"),
    }


def format_source_freshness_badge(
    last_verified: str | None = None,
    source_url: str | None = None,
    *,
    reference: datetime | None = None,
) -> tuple[str, str]:
    """
    Return (label, severity) for source freshness display.
    severity: ok | warning | error
    """
    ref = reference or datetime.now()
    if not has_valid_source_url(source_url):
        return "Missing verified source", "error"
    parsed = parse_date(last_verified)
    if parsed is None:
        return f"Verified source · updated {ref.strftime('%Y-%m-%d')}", "warning"
    if is_stale(last_verified, reference=ref):
        return f"Stale source · last verified {last_verified}", "warning"
    return f"Verified source · updated {last_verified}", "ok"


def get_confidence_warnings(
    company_id: str,
    profiles_df,
    people_df,
    sources_df,
    reference: datetime | None = None,
    projects_df=None,
    insights_df=None,
) -> list[str]:
    """Return human-readable warnings for a company."""
    warnings: list[str] = []
    if sources_df is not None and not sources_df.empty:
        src_count = len(sources_df[sources_df["company_id"] == company_id])
    else:
        src_count = 0
    if src_count == 0:
        warnings.append("No research_sources rows — add public citations before outreach.")

    if profiles_df is not None and not profiles_df.empty:
        prof = profiles_df[profiles_df["company_id"] == company_id]
        if not prof.empty:
            lu = prof.iloc[0].get("last_updated", "")
            if is_stale(lu, reference=reference):
                warnings.append(f"Company profile last_updated ({lu}) is stale (>30 days).")

    if people_df is not None and not people_df.empty:
        subset = people_df[people_df["company_id"] == company_id]
        placeholders = subset[subset["verification_status"].str.lower() == "placeholder"]
        if len(placeholders) == len(subset) and len(subset) > 0:
            warnings.append(
                "No verified contacts — use careers link from research_sources before outreach."
            )

    if profiles_df is not None and not profiles_df.empty:
        prof = profiles_df[profiles_df["company_id"] == company_id]
        if not prof.empty and "source_urls" in prof.columns:
            urls = str(prof.iloc[0].get("source_urls", ""))
            if not has_valid_source_url(urls.split(",")[0].strip() if urls else ""):
                warnings.append("Missing verified source — company profile lacks source_urls.")

    if projects_df is not None and not projects_df.empty:
        proj = projects_df[projects_df["company_id"] == company_id]
        if "source_url" in proj.columns and len(proj) > 0:
            missing_count = int((~proj["source_url"].apply(has_valid_source_url)).sum())
            if missing_count:
                warnings.append(f"{missing_count} company project(s) missing verified source_url.")

    if insights_df is not None and not insights_df.empty:
        ins = insights_df[insights_df["company_id"] == company_id]
        if len(ins) == 0:
            warnings.append("No interview insights — add verified questions to interview_insights.csv.")
        elif "source_url" in ins.columns:
            missing_count = int((~ins["source_url"].apply(has_valid_source_url)).sum())
            if missing_count:
                warnings.append(f"{missing_count} interview insight(s) missing verified source_url.")

    return warnings
