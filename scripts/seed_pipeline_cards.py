#!/usr/bin/env python3
"""Seed pipeline_cards.csv from intelligence data."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_all
from src.pipeline_engine import build_pipeline_cards, save_pipeline_cards


def main() -> int:
    data = load_all()
    cards = build_pipeline_cards(data)
    path = save_pipeline_cards(cards)
    print(f"Saved {len(cards)} pipeline cards to {path}")
    if cards:
        top = cards[0]
        print(f"Top card: {top['company_name']} — {top['job_title']} (priority {top['priority_score']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
