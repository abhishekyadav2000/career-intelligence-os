"""Relationship graph XLSX export — 8-tab workbook (v1.3)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.contact_pod_builder import load_contact_pods
from src.demand_intelligence_engine import load_demand_signals
from src.engagement_engine import load_outreach_queue
from src.knowledge_graph import load_edges
from src.role_demand_scorer import load_role_demand_scores

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EXPORT_DIR = DATA_DIR / "relationship_graph_export"
DEFAULT_OUTPUT = EXPORT_DIR / "DFW_Company_Relationship_Graph.xlsx"


def export_relationship_graph_xlsx(
    data: dict | None = None,
    output_path: Path | str | None = None,
) -> Path:
    """
    Export 8-tab relationship workbook:
    Companies, Jobs, People, Evidence, Outreach Queue, Interaction Log,
    Portfolio Match, Knowledge Graph Edges.
    """
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise ImportError("openpyxl required for XLSX export") from exc

    out = Path(output_path) if output_path else DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)

    companies_df = (data or {}).get("companies", pd.DataFrame())
    jobs_df = (data or {}).get("jobs", pd.DataFrame())
    proof_df = (data or {}).get("proof_assets", pd.DataFrame())
    people_df = (data or {}).get("people_map", pd.DataFrame())

    demand_signals = load_demand_signals()
    role_scores = load_role_demand_scores()
    pods = load_contact_pods()
    outreach = pd.DataFrame(load_outreach_queue())
    edges = load_edges()

    conv_path = DATA_DIR / "conversation_log_template.csv"
    interaction = pd.read_csv(conv_path) if conv_path.exists() else pd.DataFrame()

    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        if not companies_df.empty:
            companies_df.to_excel(writer, sheet_name="Companies", index=False)
        else:
            pd.DataFrame({"note": ["No companies loaded"]}).to_excel(
                writer, sheet_name="Companies", index=False
            )

        jobs_out = role_scores if not role_scores.empty else jobs_df
        jobs_out.to_excel(writer, sheet_name="Jobs", index=False)

        people_out = pods if not pods.empty else people_df
        people_out.to_excel(writer, sheet_name="People", index=False)

        evidence_parts = []
        if not demand_signals.empty:
            evidence_parts.append(demand_signals)
        if not proof_df.empty:
            evidence_parts.append(proof_df)
        evidence = pd.concat(evidence_parts, ignore_index=True) if evidence_parts else pd.DataFrame()
        evidence.to_excel(writer, sheet_name="Evidence", index=False)

        outreach.to_excel(writer, sheet_name="Outreach Queue", index=False)
        interaction.to_excel(writer, sheet_name="Interaction Log", index=False)

        portfolio = proof_df if not proof_df.empty else pd.DataFrame()
        portfolio.to_excel(writer, sheet_name="Portfolio Match", index=False)
        edges.to_excel(writer, sheet_name="Knowledge Graph Edges", index=False)

    return out
