"""Register the inbox-digest schedule (12 PM weekdays).

Run:
    python -m tasks.inbox_digest
"""

from agno.scheduler import ScheduleManager

from db import get_postgres_db

mgr = ScheduleManager(get_postgres_db())

schedule = mgr.create(
    name="inbox-digest",
    cron="0 12 * * 1-5",
    endpoint="/agents/pal/runs",
    payload={
        "message": (
            "Midday inbox digest:\n"
            "1. Summarize emails from this morning — group by sender or thread.\n"
            "2. Flag anything that needs a response today.\n"
            "3. Note any action items with owners and deadlines."
        ),
    },
    timezone="America/New_York",
    description="Weekday midday email digest (requires Gmail)",
    if_exists="update",
)

print(f"Schedule ready: {schedule.name} (next run: {schedule.next_run_at})")
