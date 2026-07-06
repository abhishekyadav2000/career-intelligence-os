"""Grouped navigation configuration for Career Intelligence OS v1.2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "feature_registry.yaml"

NAV_GROUPS: dict[str, list[str]] = {
    "Execute": ["Demand First", "Mission Control"],
    "Prepare": ["Interview Simulator", "My Profile & Portfolio"],
    "Intelligence": ["Company 360", "Role Deep Dive", "People Map", "Proof Assets"],
    "Analytics": ["Company Ranking", "Role Fit", "Sponsorship Signal", "Recommendations", "Overview"],
    "Tools": [
        "Command Center",
        "Networking Map",
        "Interview Prep",
        "Export",
        "Conversation Feedback",
    ],
}

NAV_GROUP_ORDER = ["Execute", "Prepare", "Intelligence", "Analytics", "Tools"]


def load_feature_registry(path: Path | None = None) -> dict[str, Any]:
    """Load feature_registry.yaml for help tooltips."""
    fpath = path or REGISTRY_PATH
    if not fpath.exists():
        return {"features": {}}
    with open(fpath, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"features": {}}


def get_feature_help(feature_key: str, registry: dict[str, Any] | None = None) -> str:
    """Return description text for a feature (for st.help / captions)."""
    reg = registry or load_feature_registry()
    feat = reg.get("features", {}).get(feature_key, {})
    parts = [feat.get("description", "")]
    sources = feat.get("data_sources") or []
    if sources:
        parts.append(f"Sources: {', '.join(sources)}")
    refresh = feat.get("refresh_frequency")
    if refresh:
        parts.append(f"Refresh: {refresh}")
    return " · ".join(p for p in parts if p)


def feature_key_for_tab(tab_name: str) -> str:
    """Map display tab name to registry key."""
    mapping = {
        "Demand First": "demand_first",
        "Mission Control": "mission_control",
        "Interview Simulator": "interview_simulator",
        "My Profile & Portfolio": "my_profile",
        "Company 360": "company_360",
        "Role Deep Dive": "role_deep_dive",
        "People Map": "people_map",
        "Proof Assets": "proof_assets",
        "Company Ranking": "company_ranking",
        "Role Fit": "role_fit",
        "Sponsorship Signal": "sponsorship_signal",
        "Recommendations": "recommendations",
        "Overview": "mission_control",
        "Command Center": "command_center",
        "Networking Map": "networking_map",
        "Interview Prep": "interview_prep",
        "Export": "export",
        "Conversation Feedback": "conversation_feedback",
    }
    return mapping.get(tab_name, tab_name.lower().replace(" ", "_"))
