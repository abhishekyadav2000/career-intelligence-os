"""People and power mapping — placeholder-safe contact intelligence."""

from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CONTACT_TYPE_WEIGHTS = {
    "hiring_manager": 1.0,
    "recruiter": 0.85,
    "alumni": 0.65,
    "peer": 0.55,
}

STAGE_MULTIPLIERS = {
    "initial outreach": 0.9,
    "recruiter screen": 1.0,
    "hiring manager screen": 1.15,
    "technical interview": 1.1,
    "final round": 1.05,
    "follow-up": 0.95,
}

CONVERSATION_TYPE_TARGETS = {
    "recruiter": ["recruiter"],
    "hiring manager": ["hiring_manager"],
    "peer": ["peer"],
    "alumni": ["alumni"],
    "informational": ["peer", "alumni"],
}


def load_people_map() -> pd.DataFrame:
    path = DATA_DIR / "people_map.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def build_people_map(company_id: str, people_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Return people map for a company with computed priority scores."""
    people_df = people_df if people_df is not None else load_people_map()
    subset = people_df[people_df["company_id"] == company_id].copy()
    if subset.empty:
        return subset

    subset["effective_priority"] = subset.apply(
        lambda r: score_contact_priority(r, "informational", "recruiter screen"),
        axis=1,
    )
    return subset.sort_values("hiring_power_score", ascending=False)


def score_contact_priority(
    person_row: pd.Series | dict,
    conversation_type: str,
    interview_stage: str,
) -> float:
    """Score contact priority for a given conversation context."""
    if isinstance(person_row, dict):
        person_row = pd.Series(person_row)

    base = float(person_row.get("hiring_power_score", 50))
    contact_type = str(person_row.get("contact_type", "peer"))
    type_weight = CONTACT_TYPE_WEIGHTS.get(contact_type, 0.5)
    stage_mult = STAGE_MULTIPLIERS.get(interview_stage.lower(), 1.0)

    targets = CONVERSATION_TYPE_TARGETS.get(conversation_type.lower(), [])
    alignment = 1.2 if contact_type in targets else 0.85

    verification = str(person_row.get("verification_status", "source_backed"))
    verify_mult = {
        "verified": 1.0,
        "verified_public": 1.0,
        "source_backed": 0.95,
        "partial": 0.9,
        "needs_verification": 0.8,
        "placeholder": 0.75,
    }.get(verification, 0.85)

    score = base * type_weight * stage_mult * alignment * verify_mult
    return round(min(score, 100.0), 1)


def generate_person_strategy(person_row: pd.Series | dict, conversation_type: str) -> str:
    """Generate outreach strategy for a contact placeholder."""
    if isinstance(person_row, dict):
        person_row = pd.Series(person_row)

    name = person_row.get("person_name", "Careers Recruiting Team")
    contact_type = person_row.get("contact_type", "peer")
    company = person_row.get("company_name", "the company")
    verification = person_row.get("verification_status", "source_backed")

    if verification == "placeholder":
        verify_note = "Verify identity via search query before referencing by name."
    elif verification == "source_backed":
        verify_note = "Use official careers portal or team channel — do not invent individual names."
    elif verification == "verified_public":
        verify_note = "Public executive — informational context only; route applications via careers portal."
    else:
        verify_note = "Contact verified — personalize with public profile details only."

    strategies = {
        "recruiter": (
            f"Open with role fit and sponsorship transparency. Reference {company} careers portal. "
            f"Ask about process timeline. {verify_note}"
        ),
        "hiring_manager": (
            f"Lead with business problem alignment and proof-of-work demo (CI OS dashboard). "
            f"Ask about team priorities and 30/60/90 expectations. {verify_note}"
        ),
        "peer": (
            f"Request informational chat about day-to-day work — no referral ask on first message. "
            f"Learn team culture and tooling. {verify_note}"
        ),
        "alumni": (
            f"Mention shared university connection only if verified. Ask about team structure and hiring landscape. "
            f"{verify_note}"
        ),
    }

    base = strategies.get(contact_type, f"Professional outreach to {name} at {company}. {verify_note}")
    if conversation_type.lower() != contact_type and conversation_type.lower() != "informational":
        base += f" Adapt tone for {conversation_type} conversation context."
    return base


def generate_people_search_queries(company_name: str, contact_type: str) -> str:
    """Generate a LinkedIn people search URL for manual verification."""
    keywords = {
        "recruiter": f"{company_name} technology recruiter",
        "hiring_manager": f"{company_name} engineering manager",
        "peer": f"{company_name} technology analyst",
        "alumni": f"{company_name} alumni",
    }
    query = keywords.get(contact_type, f"{company_name} {contact_type}")
    return f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(query)}"


def rank_contacts_for_conversation(
    company_id: str,
    conversation_type: str,
    interview_stage: str,
    people_df: pd.DataFrame | None = None,
) -> list[dict]:
    """Rank all company contacts for a specific conversation context."""
    people_df = people_df if people_df is not None else load_people_map()
    subset = people_df[people_df["company_id"] == company_id].copy()
    if subset.empty:
        return []

    results = []
    for _, row in subset.iterrows():
        priority = score_contact_priority(row, conversation_type, interview_stage)
        results.append({
            **row.to_dict(),
            "conversation_priority": priority,
            "strategy": generate_person_strategy(row, conversation_type),
        })
    results.sort(key=lambda x: x["conversation_priority"], reverse=True)
    return results
