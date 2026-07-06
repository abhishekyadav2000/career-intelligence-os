"""Tests for knowledge graph."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.knowledge_graph import export_graph_summary, get_proof_path, load_edges, query_neighbors


def test_load_edges():
    df = load_edges()
    assert not df.empty
    assert "relationship" in df.columns


def test_query_neighbors():
    edges = query_neighbors("JPMorgan Chase")
    assert isinstance(edges, list)


def test_get_proof_path():
    path = get_proof_path("JPMorgan Chase", "Cloud / Security")
    assert isinstance(path, list)
    if path:
        assert "relationship" in path[0]


def test_export_graph_summary():
    summary = export_graph_summary("C001")
    assert summary["company_id"] == "C001"
    assert summary["edges"] > 0
