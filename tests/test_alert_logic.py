from datetime import date

from alert_logic import developers_without_plan, load_schedules


def test_load_schedules_and_detect_idle_developers():
    payload = {
        "members": [
            {
                "name": "Alice",
                "assignments": [
                    {"date": "2026-04-03"},
                ],
            },
            {
                "name": "Bob",
                "assignments": [
                    {"date": "2026-04-07"},
                ],
            },
            {
                "name": "Carol",
                "assignments": [],
            },
        ]
    }
    schedules = load_schedules(payload)
    idle = developers_without_plan(schedules, now=date(2026, 4, 3), within_days=2)
    assert idle == ["Bob", "Carol"]
