from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable


@dataclass
class DeveloperSchedule:
    name: str
    work_dates: list[date]


def _normalize_date(value: str) -> date:
    """Parse common TAPD-like date strings."""
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def load_schedules(payload: dict) -> list[DeveloperSchedule]:
    """Load schedules from payload.

    Expected format:
    {
      "members": [
        {"name": "Alice", "assignments": [{"date": "2026-04-03"}, ...]},
      ]
    }
    """
    members = payload.get("members", [])
    schedules: list[DeveloperSchedule] = []
    for member in members:
        name = str(member.get("name", "")).strip()
        if not name:
            continue
        assignments = member.get("assignments", [])
        dates: list[date] = []
        for assignment in assignments:
            raw_date = assignment.get("date")
            if raw_date:
                dates.append(_normalize_date(str(raw_date)))
        schedules.append(DeveloperSchedule(name=name, work_dates=dates))
    return schedules


def developers_without_plan(
    schedules: Iterable[DeveloperSchedule],
    now: date,
    within_days: int = 2,
) -> list[str]:
    """Return developers that have no assignment within [now, now + within_days]."""
    deadline = now + timedelta(days=within_days)
    no_plan: list[str] = []

    for schedule in schedules:
        has_plan = any(now <= d <= deadline for d in schedule.work_dates)
        if not has_plan:
            no_plan.append(schedule.name)
    return sorted(no_plan)
