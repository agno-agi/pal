# Pal - A personal context-agent that learns how you work

Pal is a single-agent context system built with [Agno](https://docs.agno.com). It
navigates a heterogeneous graph of sources - SQL, local context files, Gmail,
Google Calendar, and web search to complete tasks and improve retrieval quality
over time.

## How It Works

Pal is designed as a context agent, not a static memory dump. It follows:

1. **Classify** intent from the user request.
2. **Recall** from knowledge, learnings, and files with intent scope.
3. **Retrieve** from the right sources.
4. **Act** through tool calls.
5. **Learn** so the next request is better.

It uses per-source summarization before synthesis, which scales as context grows.

## Context Graph

| Source | Purpose | Always available |
|--------|---------|-----------------|
| SQL (`pal_*`) | Structured notes, people, projects, etc. | Yes |
| Files (`context/`) | Persistent context: voice, templates, briefs, notes | Yes |
| Gmail | Thread search, reading, draft creation | Requires Google credentials |
| Calendar | Event lookup/create/update | Requires Google credentials |
| Exa | Web research | Requires `EXA_API_KEY` |

## Recursive Context Navigation

When a query touches many rows, files, emails, or events:

- Summarize SQL results per source before mixing
- Summarize thread segments and long files in chunks
- Synthesize across per-source summaries instead of dumping everything into one
  response

This is the major quality lever in Pal's execution model.

## Files and Context Directory

Pal's files are the **primary context territory**.

- Location: `PAL_CONTEXT_DIR` (default `./context`)
- Search and read files on demand from this directory
- Write summaries/exports back to files
- File deletion is disabled for safety

The shipped voice templates in `context/voice/` are read as guidance:

- `x-post.md`
- `linkedin-post.md`
- `email.md`

Because files are not centrally embedded, edits are immediately reflected without
reindexing.

## Quick Start

```sh
cp example.env .env
# Add OPENAI_API_KEY and optional capability keys
docker compose up -d --build
```

Open `http://localhost:8000/docs` and add the endpoint to the AgentOS UI at
[os.agno.com](https://os.agno.com).

## Context Loading

If your repo includes `scripts/load_context.py`, preload files and manifests:

```sh
python scripts/load_context.py
python scripts/load_context.py --recreate  # drop and reload
```

## Capabilities

Pal starts with SQL + Files and enables more as env vars are added.

### Exa Web Research

Add:

```env
EXA_API_KEY=your-exa-key
```

### Gmail + Google Calendar

Add:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_PROJECT_ID=your-google-project-id
```

### Slack Interface (AgentOS)

Add:

```env
SLACK_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

Threads map to Slack thread IDs for separate contexts.

## Quick Prompts

```text
Save a note: Met with Sarah Chen from Acme Corp. She's interested in a partnership.
What do I know about Sarah?
Check my latest emails
What's on my calendar this week?
Draft an X post in my voice about AI productivity
Save a summary of today's meeting to meeting-notes.md
What do I know about Project X?
Research web trends on AI productivity
```

## Dynamic Tool Registration (code-level)

```python
from agno.tools.file import FileTools
from agno.tools.mcp import MCPTools
from agno.tools.sql import SQLTools
from pal.tools import create_update_knowledge

tools = [
    SQLTools(db_url=db_url),
    FileTools(base_dir=PAL_CONTEXT_DIR, enable_delete_file=False),
    create_update_knowledge(pal_knowledge),
]

if EXA_API_KEY:
    tools.append(MCPTools(url=EXA_MCP_URL))

if GOOGLE_CLIENT_ID:
    tools.append(GmailTools(exclude_tools=["send_email", "send_email_reply"]))
    tools.append(GoogleCalendarTools(allow_update=True))
```

## Data Storage

| Storage | What goes there |
|---|---|
| PostgreSQL | `pal_*` tables, `pal_contents`, `pal_knowledge`, `pal_learnings` |
| `context/` | Files for voice, preferences, briefs, exports |

## Troubleshooting

### I can't access X

- **Web search**: add `EXA_API_KEY` and restart.
- **Gmail**: add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_PROJECT_ID` and restart.
- **Calendar**: add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_PROJECT_ID` and restart.

### Common checks

- `docker compose config` should show optional vars with fallback defaults.
- `PAL_CONTEXT_DIR` should be mounted to `./context`.
- If context prompts stop making sense, rerun `python scripts/load_context.py`.

## Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT-5.2 |
| `EXA_API_KEY` | No | `""` | Exa web search |
| `GOOGLE_CLIENT_ID` | No | `""` | Gmail + Calendar |
| `GOOGLE_CLIENT_SECRET` | No | `""` | Gmail + Calendar |
| `GOOGLE_PROJECT_ID` | No | `""` | Gmail + Calendar |
| `PAL_CONTEXT_DIR` | No | `./context` | Context directory for FileTools |
| `SLACK_TOKEN` | No | `""` | Optional Slack interface |
| `SLACK_SIGNING_SECRET` | No | `""` | Optional Slack interface |
| `PORT` | No | `8000` | API port |
| `DB_HOST` | No | `localhost` | DB host |
| `DB_PORT` | No | `5432` | DB port |
| `DB_USER` | No | `ai` | DB user |
| `DB_PASS` | No | `ai` | DB password |
| `DB_DATABASE` | No | `ai` | DB name |
| `RUNTIME_ENV` | No | `prd` | Use `dev` for reload |

## Links

- [Agno Docs](https://docs.agno.com)
- [AgentOS Docs](https://docs.agno.com/agent-os/introduction)
- [Recursive Language Models](https://arxiv.org/abs/2512.24601)
