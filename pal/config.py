from os import getenv
from pathlib import Path

from pal.paths import CONTEXT_DIR

# Core
PAL_CONTEXT_DIR = Path(getenv("PAL_CONTEXT_DIR", str(CONTEXT_DIR)))

# Exa
EXA_API_KEY = getenv("EXA_API_KEY", "")
EXA_MCP_URL = (
    f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}&tools=web_search_exa"
    if EXA_API_KEY
    else "https://mcp.exa.ai/mcp?tools=web_search_exa"
)

# Slack
SLACK_TOKEN = getenv("SLACK_TOKEN", "")

# Google — OAuth (all 3 required) OR service account
GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_PROJECT_ID = getenv("GOOGLE_PROJECT_ID", "")
GOOGLE_SERVICE_ACCOUNT_FILE = getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
GOOGLE_INTEGRATION_ENABLED = bool(
    (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_PROJECT_ID)
    or GOOGLE_SERVICE_ACCOUNT_FILE
)
