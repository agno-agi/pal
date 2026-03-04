"""Register the weekly-review schedule (5 PM Friday).

Run:
    python -m tasks.weekly_review
"""

from agno.scheduler import ScheduleManager

from db import get_postgres_db

mgr = ScheduleManager(get_postgres_db())

schedule = mgr.create(
    name="weekly-review",
    cron="0 17 * * 5",
    endpoint="/agents/pal/runs",
    payload={
        "message": (
            "It's Friday — time for a weekly review.\n"
            "1. Read context/templates/weekly-review.md for the structure.\n"
            "2. Fill it in based on this week's conversations, decisions, and action items.\n"
            "3. Save the draft to context/meetings/ using the filename format "
            "YYYY-MM-DD - weekly-review.md (use today's date).\n\n"
            "When done, post a summary of the weekly review to the #pal-updates Slack channel."
        ),
    },
    timezone="America/New_York",
    description="Friday afternoon weekly review draft",
    if_exists="update",
)

print(f"Schedule ready: {schedule.name} (next run: {schedule.next_run_at})")
