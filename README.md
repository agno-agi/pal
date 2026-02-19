# Pal

A personal agent that learns your preferences, context, and history. Built with [Agno](https://docs.agno.com).

Pal creates SQL tables on demand, remembers everything you tell it, and gets better over time using LearningMachine. It connects notes, people, bookmarks, and anything else you want to track.

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| Pal | SQL + Exa MCP + LearningMachine | Personal knowledge system that dynamically creates schemas, searches the web, and learns your preferences. |

## Get Started

```sh
# Clone the repo
cp example.env .env
# Edit .env and add your OPENAI_API_KEY and EXA_API_KEY

# Start the application
docker compose up -d --build
```

Confirm Pal is running at [http://localhost:8000/docs](http://localhost:8000/docs).

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com) and login
2. Add OS → Local → `http://localhost:8000`
3. Click "Connect"

**Try it:**

```
Save a note: Met with Sarah Chen from Acme Corp
What do I know about Sarah?
Create a projects table and track my current projects
```

## Deploy to Railway

Requires:
- [Railway CLI](https://docs.railway.com/guides/cli)
- `OPENAI_API_KEY` set in your environment

```sh
railway login

./scripts/railway_up.sh
```

The script provisions PostgreSQL, configures environment variables, and deploys your application.

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" → "Live"
3. Enter your Railway domain

### Manage deployment

```sh
railway logs --service pal      # View logs
railway open                    # Open dashboard
railway up --service pal -d     # Update after changes
```

To stop services:
```sh
railway down --service pal
railway down --service pgvector
```

## How Pal Works

**SQL Database** — Pal's structured storage for your data. Notes, bookmarks, people, projects, decisions — tables are created on demand with a `pal_` prefix. Uses `SQLTools` against the shared PostgreSQL database.

**LearningMachine** — Meta-knowledge about you and the database. Preferences, patterns, schemas created, query patterns that work. Stored in a separate vector knowledge base (`pal_learnings`).

**Exa MCP** — Web research via the Exa search API. Pal can look things up and optionally save findings to the database.

## Project Structure

```
├── pal/
│   └── agent.py              # Pal agent implementation
├── app/
│   ├── main.py               # AgentOS entry point
│   └── config.yaml           # Quick prompts config
├── db/
│   ├── session.py            # PostgreSQL database helpers
│   └── url.py                # Connection URL builder
├── scripts/                  # Helper scripts
├── compose.yaml              # Docker Compose config
├── Dockerfile
└── pyproject.toml            # Dependencies
```

## Common Tasks

### Add tools to Pal

Agno includes 100+ tool integrations. See the [full list](https://docs.agno.com/tools/toolkits).

```python
from agno.tools.slack import SlackTools

pal = Agent(
    ...
    tools=[
        SQLTools(db_url=db_url),
        MCPTools(url=EXA_MCP_URL),
        SlackTools(),
    ],
)
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements: `./scripts/generate_requirements.sh`
3. Rebuild: `docker compose up -d --build`

### Use a different model provider

1. Add your API key to `.env` (e.g., `ANTHROPIC_API_KEY`)
2. Update `pal/agent.py` to use the new provider:

```python
from agno.models.anthropic import Claude

model=Claude(id="claude-sonnet-4-5")
```
3. Add dependency: `anthropic` in `pyproject.toml`

---

## Local Development

For development without Docker:

```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Start PostgreSQL (required)
docker compose up -d pal-db

# Run the app
python -m app.main
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `EXA_API_KEY` | No | - | Exa API key for web research |
| `PORT` | No | `8000` | API server port |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Agno Discord](https://agno.com/discord)
