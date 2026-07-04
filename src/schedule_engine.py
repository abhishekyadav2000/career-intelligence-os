"""Schedule engine — Monday launch plan and daily activity queue."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LAUNCH_PLAN_PATH = DATA_DIR / "monday_launch_plan.csv"
ACTIVITY_SCHEDULE_PATH = DATA_DIR / "activity_schedule.csv"

LAUNCH_PLAN_COLUMNS = [
    "plan_date",
    "day_name",
    "focus",
    "key_outputs",
    "success_metrics",
    "status",
    "notes",
]

ACTIVITY_COLUMNS = [
    "activity_id",
    "day_of_week",
    "start_time",
    "activity_name",
    "description",
    "category",
    "duration_minutes",
    "status",
    "linked_pipeline_stage",
]


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def load_launch_plan(path: Path | None = None) -> list[dict]:
    return _read_csv(path or LAUNCH_PLAN_PATH)


def load_activity_schedule(path: Path | None = None) -> list[dict]:
    return _read_csv(path or ACTIVITY_SCHEDULE_PATH)


def _parse_date(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value[:10], fmt)
        except ValueError:
            continue
    return None


def _parse_time(value: str) -> tuple[int, int]:
    """Return (hour, minute) from strings like '9:00 AM' or '09:00'."""
    value = (value or "").strip().upper()
    for fmt in ("%I:%M %p", "%H:%M", "%I:%M%p"):
        try:
            dt = datetime.strptime(value.replace(" ", ""), fmt.replace(" ", ""))
            return dt.hour, dt.minute
        except ValueError:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.hour, dt.minute
            except ValueError:
                continue
    return 0, 0


def get_daily_plan(date: datetime | str | None = None, plan: list[dict] | None = None) -> dict | None:
    ref = date if isinstance(date, datetime) else (
        _parse_date(str(date)) if date else datetime.now()
    )
    if ref is None:
        ref = datetime.now()
    plan = plan if plan is not None else load_launch_plan()
    date_str = ref.strftime("%Y-%m-%d")
    for row in plan:
        if row.get("plan_date", "")[:10] == date_str:
            return row
    return None


def get_overdue_activities(
    reference: datetime | None = None,
    schedule: list[dict] | None = None,
) -> list[dict]:
    ref = reference or datetime.now()
    schedule = schedule if schedule is not None else load_activity_schedule()
    day_name = ref.strftime("%A")
    overdue = []
    for act in schedule:
        if act.get("day_of_week", "").lower() != day_name.lower():
            continue
        if act.get("status", "pending").lower() == "done":
            continue
        hour, minute = _parse_time(act.get("start_time", ""))
        act_dt = ref.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if act_dt < ref:
            overdue.append(act)
    return overdue


def get_next_activities(
    reference: datetime | None = None,
    schedule: list[dict] | None = None,
    limit: int = 5,
) -> list[dict]:
    ref = reference or datetime.now()
    schedule = schedule if schedule is not None else load_activity_schedule()
    day_name = ref.strftime("%A")
    upcoming = []
    for act in schedule:
        if act.get("day_of_week", "").lower() != day_name.lower():
            continue
        if act.get("status", "pending").lower() == "done":
            continue
        hour, minute = _parse_time(act.get("start_time", ""))
        act_dt = ref.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if act_dt >= ref:
            upcoming.append({**act, "_sort_time": act_dt})
    upcoming.sort(key=lambda a: a["_sort_time"])
    return [{k: v for k, v in a.items() if k != "_sort_time"} for a in upcoming[:limit]]


def mark_activity_done(activity_id: str, path: Path | None = None) -> bool:
    p = path or ACTIVITY_SCHEDULE_PATH
    rows = load_activity_schedule(p)
    found = False
    for row in rows:
        if row.get("activity_id") == activity_id:
            row["status"] = "done"
            found = True
    if found:
        _write_csv(p, rows, ACTIVITY_COLUMNS)
    return found


def summarize_week_plan(plan: list[dict] | None = None) -> dict:
    plan = plan if plan is not None else load_launch_plan()
    if not plan:
        return {"days": 0, "entries": [], "monday_focus": ""}
    monday = next((p for p in plan if p.get("day_name", "").lower() == "monday"), None)
    return {
        "days": len(plan),
        "entries": plan,
        "monday_focus": monday.get("focus", "") if monday else "",
        "monday_outputs": monday.get("key_outputs", "") if monday else "",
        "monday_metrics": monday.get("success_metrics", "") if monday else "",
    }
