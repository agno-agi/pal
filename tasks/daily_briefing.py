"""Register the daily-briefing schedule (8 AM weekdays).

Run:
    python -m tasks.daily_briefing
"""

from agno.scheduler import ScheduleManager

from db import get_postgres_db

mgr = ScheduleManager(get_postgres_db())

schedule = mgr.create(
    name="daily-briefing",
    cron="0 8 * * 1-5",
    endpoint="/agents/pal/runs",
    payload={
        "message": (
            "Good morning. Give me a quick briefing to start the day:\n"
            "1. Check today's calendar — list events with times, flag any that need prep.\n"
            "2. Summarize unread or flagged emails (if Gmail is enabled).\n"
            "3. List my open priorities and action items from recent conversations.\n"
            "Keep it short — a morning scan, not a full report.\n\n"
            "When done, post the briefing to the #pal-updates Slack channel."
        ),
    },
    timezone="America/New_York",
    description="Weekday morning briefing — calendar, emails, priorities",
    if_exists="update",
)

print(f"Schedule ready: {schedule.name} (next run: {schedule.next_run_at})")
