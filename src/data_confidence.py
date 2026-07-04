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


def get_confidence_warnings(
    company_id: str,
    profiles_df,
    people_df,
    sources_df,
    reference: datetime | None = None,
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

    return warnings
