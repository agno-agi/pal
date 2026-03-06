"""Register the context-refresh schedule (8 AM daily).

Run:
    python -m tasks.context_refresh
"""

from agno.scheduler import ScheduleManager

from db import get_postgres_db

mgr = ScheduleManager(get_postgres_db())

schedule = mgr.create(
    name="context-refresh",
    cron="0 8 * * *",
    endpoint="/context/reload",
    payload={},
    timezone="America/New_York",
    description="Daily context file re-index",
    if_exists="update",
)

print(f"Schedule ready: {schedule.name} (next run: {schedule.next_run_at})")
