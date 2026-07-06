"""Knowledge graph — company → role → skill → proof chains (v1.3)."""

from __future__ import annotations

import csv
from pathlib import Path
from uuid import uuid4

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EDGES_PATH = DATA_DIR / "knowledge_graph_edges.csv"

EDGE_COLUMNS = [
    "edge_id",
    "from_entity",
    "from_type",
    "relationship",
    "to_entity",
    "to_type",
    "confidence",
    "source_url",
]

VALID_RELATIONSHIPS = {
    "HAS_ROLE",
    "REQUIRES",
    "WORKS_AT",
    "MAY_RELATE_TO",
    "DEMONSTRATES",
    "HAS_SIGNAL",
    "TARGETS",
}


def load_edges(path: Path | None = None) -> pd.DataFrame:
    p = path or EDGES_PATH
    if not p.exists():
        return pd.DataFrame(columns=EDGE_COLUMNS)
    return pd.read_csv(p)


def add_edge(
    from_entity: str,
    from_type: str,
    relationship: str,
    to_entity: str,
    to_type: str,
    confidence: float = 0.8,
    source_url: str = "",
    path: Path | None = None,
) -> dict:
    """Append one edge to the knowledge graph CSV."""
    if relationship not in VALID_RELATIONSHIPS:
        raise ValueError(f"Invalid relationship: {relationship}")

    edge = {
        "edge_id": f"KG-{uuid4().hex[:8].upper()}",
        "from_entity": from_entity,
        "from_type": from_type,
        "relationship": relationship,
        "to_entity": to_entity,
        "to_type": to_type,
        "confidence": confidence,
        "source_url": source_url,
    }
    p = path or EDGES_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    write_header = not p.exists() or p.stat().st_size == 0
    with p.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EDGE_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(edge)
    return edge


def query_neighbors(entity: str, relationship: str | None = None) -> list[dict]:
    """Find edges where entity appears as from or to."""
    df = load_edges()
    if df.empty:
        return []
    mask = (df["from_entity"] == entity) | (df["to_entity"] == entity)
    subset = df[mask]
    if relationship:
        subset = subset[subset["relationship"] == relationship]
    return subset.to_dict("records")


def get_proof_path(company: str, role_family: str) -> list[dict]:
    """
    Return company → role → skill → portfolio asset chain.
    Walks HAS_ROLE, REQUIRES, DEMONSTRATES edges.
    """
    df = load_edges()
    if df.empty:
        return []

    chain: list[dict] = []
    company_edges = df[(df["from_entity"] == company) & (df["relationship"] == "HAS_ROLE")]
    roles = company_edges["to_entity"].tolist()

    for role in roles:
        chain.append({
            "step": "company→role",
            "from": company,
            "to": role,
            "relationship": "HAS_ROLE",
        })
        skill_edges = df[(df["from_entity"] == role) & (df["relationship"] == "REQUIRES")]
        for _, se in skill_edges.iterrows():
            skill = se["to_entity"]
            chain.append({
                "step": "role→skill",
                "from": role,
                "to": skill,
                "relationship": "REQUIRES",
            })
            proof_edges = df[(df["from_entity"] == skill) & (df["relationship"] == "DEMONSTRATES")]
            for _, pe in proof_edges.iterrows():
                chain.append({
                    "step": "skill→proof",
                    "from": skill,
                    "to": pe["to_entity"],
                    "relationship": "DEMONSTRATES",
                    "source_url": pe.get("source_url", ""),
                })

    if not chain and role_family:
        rf_edges = df[
            (df["from_entity"] == company)
            & (df["to_entity"].str.contains(role_family[:20], case=False, na=False))
        ]
        chain = rf_edges.to_dict("records")

    return chain


def export_graph_summary(company_id: str) -> dict:
    """Summarize knowledge graph for one company."""
    df = load_edges()
    if df.empty:
        return {"company_id": company_id, "edges": 0, "roles": [], "skills": [], "proof_assets": []}

    company_name_map = {"C001": "JPMorgan Chase"}
    company = company_name_map.get(company_id, company_id)
    related = df[
        (df["from_entity"].str.contains(company, case=False, na=False))
        | (df["to_entity"].str.contains(company, case=False, na=False))
        | (df["from_entity"] == company_id)
        | (df["to_entity"] == company_id)
    ]

    roles = related[related["relationship"] == "HAS_ROLE"]["to_entity"].unique().tolist()
    skills = related[related["relationship"] == "REQUIRES"]["to_entity"].unique().tolist()
    proofs = related[related["relationship"] == "DEMONSTRATES"]["to_entity"].unique().tolist()
    signals = related[related["relationship"] == "HAS_SIGNAL"]["to_entity"].unique().tolist()

    return {
        "company_id": company_id,
        "edges": len(related),
        "roles": roles,
        "skills": skills,
        "proof_assets": proofs,
        "signals": signals,
    }
