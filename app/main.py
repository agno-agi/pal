"""
Pal AgentOS
-----------

The main entry point for Pal.

Run:
    python -m app.main
"""

from os import getenv
from pathlib import Path

from agno.os import AgentOS

from db import get_postgres_db
from pal.agent import pal

# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------
SLACK_TOKEN = getenv("SLACK_TOKEN", "")
SLACK_SIGNING_SECRET = getenv("SLACK_SIGNING_SECRET", "")

interfaces: list = []
if SLACK_TOKEN and SLACK_SIGNING_SECRET:
    from agno.os.interfaces.slack import Slack

    interfaces.append(
        Slack(
            agent=pal,
            streaming=True,
            token=SLACK_TOKEN,
            signing_secret=SLACK_SIGNING_SECRET,
        )
    )

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Pal",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[pal],
    interfaces=interfaces,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
