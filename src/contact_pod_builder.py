"""Contact pod builder — 15-slot people map with search URLs only (v1.3)."""

from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import quote

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONTACT_PODS_PATH = DATA_DIR / "contact_pods.csv"

POD_SLOTS = [
    ("recruiter", 3, "Talent acquisition outreach"),
    ("hiring_manager", 3, "Hiring manager / team lead"),
    ("peer_similar_role", 4, "Peer in similar role family"),
    ("dfw_local", 2, "DFW-local technology contact"),
    ("alumni_connection", 2, "UNT / alumni pathway"),
    ("thought_leader", 1, "Technology thought leader"),
]

POD_COLUMNS = [
    "pod_id",
    "company_id",
    "company_name",
    "person_id",
    "person_name",
    "person_title",
    "person_type",
    "pod_slot",
    "pod_purpose",
    "location",
    "verification_status",
    "public_profile_url",
    "search_query_url",
    "engagement_hook_id",
    "engagement_level",
    "priority_score",
    "status",
    "notes",
    "last_updated",
]


def generate_people_search_urls(
    company: str,
    role_family: str = "",
    person_type: str = "recruiter",
    location: str = "Dallas OR Plano OR Irving",
) -> dict[str, str]:
    """Generate Google + LinkedIn search URL templates (no scraping)."""
    type_queries = {
        "recruiter": f'"{company}" "talent acquisition" OR recruiter {location}',
        "hiring_manager": f'"{company}" "engineering manager" OR "hiring manager" {location}',
        "peer_similar_role": f'"{company}" "{role_family or "technology analyst"}" {location}',
        "dfw_local": f'"{company}" technology {location}',
        "alumni_connection": f'"{company}" "University of North Texas" OR UNT alumni {location}',
        "thought_leader": f'"{company}" "chief information" OR "head of technology" {location}',
    }
    query = type_queries.get(person_type, type_queries["recruiter"])
    google_url = f"https://www.google.com/search?q={quote(query)}"
    linkedin_url = (
        "https://www.linkedin.com/search/results/people/?keywords="
        + quote(query.replace('"', ""))
    )
    return {"google": google_url, "linkedin": linkedin_url}


def build_pod_template(
    company_id: str,
    company_name: str,
    role_family: str = "Cloud / Security / Data / AI / Analyst",
    location: str = "Dallas OR Plano",
    reference_date: str = "",
) -> list[dict]:
    """Build 15-slot pod structure with search URLs — no fake names."""
    from datetime import datetime

    ref = reference_date or datetime.now().strftime("%Y-%m-%d")
    pods: list[dict] = []
    slot_num = 0
    for person_type, count, purpose in POD_SLOTS:
        for i in range(1, count + 1):
            slot_num += 1
            urls = generate_people_search_urls(company_name, role_family, person_type, location)
            pods.append({
                "pod_id": f"POD-{company_id}-{slot_num:02d}",
                "company_id": company_id,
                "company_name": company_name,
                "person_id": "",
                "person_name": f"[Search: {person_type.replace('_', ' ')} #{i}]",
                "person_title": "",
                "person_type": person_type,
                "pod_slot": f"{person_type}_{i}",
                "pod_purpose": purpose,
                "location": location,
                "verification_status": "placeholder",
                "public_profile_url": "",
                "search_query_url": urls["linkedin"],
                "engagement_hook_id": "",
                "engagement_level": _default_engagement_level(person_type),
                "priority_score": _pod_priority(person_type, i),
                "status": "search_needed",
                "notes": f"Use search URL to find and verify contact. Google: {urls['google']}",
                "last_updated": ref,
            })
    return pods


def _default_engagement_level(person_type: str) -> int:
    return {
        "recruiter": 3,
        "hiring_manager": 5,
        "peer_similar_role": 4,
        "dfw_local": 3,
        "alumni_connection": 6,
        "thought_leader": 2,
    }.get(person_type, 3)


def _pod_priority(person_type: str, index: int) -> int:
    base = {
        "recruiter": 85,
        "hiring_manager": 80,
        "peer_similar_role": 70,
        "dfw_local": 65,
        "alumni_connection": 75,
        "thought_leader": 55,
    }.get(person_type, 60)
    return max(50, base - (index - 1) * 3)


def score_pod_contact(row: dict) -> float:
    """Score a pod contact row for outreach priority."""
    base = float(row.get("priority_score", 50))
    status = str(row.get("verification_status", "placeholder")).lower()
    if status == "verified_public":
        base += 15
    elif status == "source_backed":
        base += 8
    engagement = int(row.get("engagement_level", 3))
    return min(100, base + engagement)


def get_pod_for_company(company_id: str, path: Path | None = None) -> list[dict]:
    """Load contact pod slots for a company."""
    p = path or CONTACT_PODS_PATH
    if not p.exists():
        return build_pod_template(company_id, company_id)
    df = pd.read_csv(p)
    if df.empty:
        return []
    subset = df[df["company_id"] == company_id]
    return subset.to_dict("records")


def load_contact_pods(path: Path | None = None) -> pd.DataFrame:
    p = path or CONTACT_PODS_PATH
    if not p.exists():
        return pd.DataFrame(columns=POD_COLUMNS)
    return pd.read_csv(p)


def save_contact_pods(pods: list[dict], path: Path | None = None) -> Path:
    p = path or CONTACT_PODS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=POD_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in pods:
            writer.writerow({col: row.get(col, "") for col in POD_COLUMNS})
    return p


def pod_completeness(company_id: str) -> dict:
    """Check if pod has verified contacts vs placeholders."""
    pods = get_pod_for_company(company_id)
    if not pods:
        return {"complete": False, "total": 0, "verified": 0, "placeholder": 0}
    verified = sum(
        1 for p in pods
        if str(p.get("verification_status", "")).lower() in ("verified_public", "verified", "source_backed")
        and not str(p.get("person_name", "")).startswith("[Search:")
    )
    placeholders = len(pods) - verified
    return {
        "complete": len(pods) >= 15 and verified >= 3,
        "total": len(pods),
        "verified": verified,
        "placeholder": placeholders,
    }
