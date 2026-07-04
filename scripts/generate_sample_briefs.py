"""Pre-generate sample conversation briefs for top 5 ICC seed companies."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.conversation_brief_generator import (
    export_brief_markdown,
    generate_conversation_brief,
)
from src.data_loader import load_all

SAMPLES = [
    ("C001", "J0001", "brief-jpmorgan-chase-sample.md"),
    ("C004", "J0010", "brief-citi-sample.md"),
    ("C006", "J0015", "brief-capital-one-sample.md"),
    ("C007", "J0018", "brief-toyota-sample.md"),
    ("C008", "J0020", "brief-att-sample.md"),
]


def main() -> int:
    data = load_all()
    export_dir = ROOT / "exports"
    export_dir.mkdir(exist_ok=True)

    brief_rows = []
    for company_id, job_id, filename in SAMPLES:
        brief = generate_conversation_brief(
            company_id,
            job_id,
            data["jobs"],
            conversation_type="hiring manager",
            interview_stage="hiring manager screen",
        )
        md = export_brief_markdown(brief)
        md_path = export_dir / filename
        md_path.write_text(md, encoding="utf-8")
        print(f"Wrote {md_path.name}")

        brief_rows.append({
            "brief_id": brief["brief_id"],
            "company_id": brief["company_id"],
            "company_name": brief["company_name"],
            "job_id": brief["job_id"],
            "job_title": brief["job_title"],
            "conversation_type": brief["conversation_type"],
            "interview_stage": brief["interview_stage"],
            "contact_type": brief["conversation_type"],
            "created_at": brief["created_at"],
            "status": "sample",
            "markdown_path": f"exports/{filename}",
            "notes": "Pre-generated sample brief for portfolio",
        })

    briefs_path = ROOT / "data" / "conversation_briefs.csv"
    import pandas as pd

    pd.DataFrame(brief_rows).to_csv(briefs_path, index=False)
    print(f"Seeded {len(brief_rows)} rows in conversation_briefs.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
