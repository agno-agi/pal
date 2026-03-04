"""Register the learning-summary schedule (10 AM Monday).

Run:
    python -m tasks.learning_summary
"""

from agno.scheduler import ScheduleManager

from db import get_postgres_db

mgr = ScheduleManager(get_postgres_db())

schedule = mgr.create(
    name="learning-summary",
    cron="0 10 * * 1",
    endpoint="/agents/pal/runs",
    payload={
        "message": (
            "Monday learning check-in:\n"
            "1. Query what you've learned about me recently from pal_learnings.\n"
            "2. Summarize patterns, preferences, and insights you've picked up.\n"
            "3. Note anything that seems wrong or worth revisiting."
        ),
    },
    timezone="America/New_York",
    description="Monday morning learning system summary",
    if_exists="update",
)

print(f"Schedule ready: {schedule.name} (next run: {schedule.next_run_at})")
