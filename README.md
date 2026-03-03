# Pal

A personal context-agent that learns how you work.

Pal navigates a heterogeneous graph of sources — SQL, local files, Gmail, Google Calendar, and web search — to complete tasks and improve retrieval quality over time. Built with [Agno](https://docs.agno.com).

## How It Works

Every interaction follows the same loop:

1. **Classify** intent from the user request.
2. **Recall** from knowledge, learnings, and files — scoped to intent.
3. **Retrieve** from the right sources.
4. **Act** through tool calls.
5. **Learn** so the next request is better.

Pal uses per-source summarization before synthesis, which means broad queries ("What do I know about Project X?") scale as context grows — each source is summarized independently, then synthesized into a final answer.

## Quick Start

```sh
# Clone the repo
git clone https://github.com/agno-agi/pal
cd pal

# Add OPENAI_API_KEY
cp example.env .env
# Edit .env and add your key

# Start the application
docker compose up -d --build

# Load context file metadata into the knowledge map
docker compose exec pal-api python context/load_context.py
```

Confirm Pal is running at [http://localhost:8000/docs](http://localhost:8000/docs).

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com) and login
2. Add OS → Local → `http://localhost:8000`
3. Click "Connect"

## Context Directory

The context directory (`PAL_CONTEXT_DIR`, default `./context`) is Pal's primary document store. Files are searched and read on demand — not centrally embedded — so edits are immediately reflected without reindexing.

**User → Pal**: Place voice guidelines, preferences, templates, and references here. Pal reads them to shape its behavior.

**Pal → User**: Pal writes summaries, exports, and generated documents back here.

```
context/
├── voice/                  # Writing tone guides per channel
│   ├── email.md
│   ├── linkedin-post.md
│   ├── x-post.md
│   ├── slack-message.md
│   └── document.md
├── preferences/            # User working-style config
│   └── general.md
├── templates/              # Document scaffolds Pal fills per use
│   ├── meeting-notes.md
│   ├── weekly-review.md
│   └── project-brief.md
└── references/             # Static context about the user
    └── about-me.md
```

File deletion is disabled at the code level.

### Context Loading

Preload file metadata into the knowledge map for retrieval routing:

```sh
python context/load_context.py
python context/load_context.py --recreate   # clear knowledge index and reload
python context/load_context.py --dry-run    # preview without writing
```

This writes compact `File:` metadata entries (intent tags, size, path) into `pal_knowledge`. File contents are still read on demand by FileTools.

## Architecture

```
AgentOS (app/main.py)  [scheduler=True, tracing=True]
 ├── FastAPI / Uvicorn
 └── Pal Agent (pal/agent.py)
     ├─ Model: GPT-5.2
     ├─ SQLTools         → PostgreSQL (pal_* tables)
     ├─ FileTools        → context/
     ├─ MCPTools         → Exa web search
     ├─ update_knowledge → custom tool (pal/tools.py)
     ├─ GmailTools       → Gmail (requires Google credentials)
     └─ CalendarTools    → Google Calendar (requires Google credentials)

     Knowledge:  pal_knowledge  (metadata map — where things are)
     Learnings:  pal_learnings  (retrieval patterns — how to navigate)
```

### Sources

| Source | Purpose | Availability |
|--------|---------|--------------|
| SQL (`pal_*`) | Structured notes, people, projects, decisions | Always |
| Files (`context/`) | Voice guides, templates, preferences, references, exports | Always |
| Exa | Web research | Always (API key optional for auth) |
| Gmail | Thread search, reading, draft creation | Requires all 3 Google credentials |
| Calendar | Event lookup, creation, updates | Requires all 3 Google credentials |

### Storage

| Layer | What goes there |
|-------|----------------|
| PostgreSQL | `pal_*` user tables, `pal_knowledge` + `pal_knowledge_contents`, `pal_learnings` + `pal_learnings_contents`, `pal_contents` |
| `context/` | Voice guides, preferences, templates, references, generated exports |

## Capabilities

Pal starts with SQL + Files + Exa and enables more as environment variables are added. When a capability isn't configured, Pal returns a specific fallback message telling the user which env vars to add — no unsupported tool calls are attempted.

### Exa Web Research

Available by default. Optionally add an API key for authenticated access:

```env
EXA_API_KEY=your-exa-key
```

### Gmail + Google Calendar

All three variables are required to enable Google integration:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_PROJECT_ID=your-google-project-id
```

Gmail is configured as draft-only — send tools are excluded at the code level. Calendar events with external attendees require user confirmation before creation.

### Slack Interface

Slack is an AgentOS-level interface, not a toolkit on the agent. It's configured in `app/main.py` and thread timestamps map to session IDs for separate conversation contexts.

```env
SLACK_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

## Example Prompts

```
Save a note: Met with Sarah Chen from Acme Corp. She's interested in a partnership.
What do I know about Sarah?
Check my latest emails
What's on my calendar this week?
Draft an X post in my voice about AI productivity
Save a summary of today's meeting to meeting-notes.md
What do I know about Project X?
Research web trends on AI productivity
```

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | — | GPT-5.2 |
| `EXA_API_KEY` | No | `""` | Exa web search auth (tool loads regardless) |
| `GOOGLE_CLIENT_ID` | No | `""` | Gmail + Calendar OAuth (all 3 required) |
| `GOOGLE_CLIENT_SECRET` | No | `""` | Gmail + Calendar OAuth (all 3 required) |
| `GOOGLE_PROJECT_ID` | No | `""` | Gmail + Calendar OAuth (all 3 required) |
| `PAL_CONTEXT_DIR` | No | `./context` | Context directory path |
| `SLACK_TOKEN` | No | `""` | Slack bot token |
| `SLACK_SIGNING_SECRET` | No | `""` | Slack signing secret |
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_USER` | No | `ai` | PostgreSQL user |
| `DB_PASS` | No | `ai` | PostgreSQL password |
| `DB_DATABASE` | No | `ai` | PostgreSQL database |
| `PORT` | No | `8000` | API port |
| `RUNTIME_ENV` | No | `prd` | `dev` enables hot reload |

## Troubleshooting

**Context prompts stop making sense**: Rerun `python context/load_context.py` to refresh the knowledge map.

**Docker config issues**: Run `docker compose config` and verify optional vars have fallback defaults.

**PAL_CONTEXT_DIR not found**: Ensure the directory is mounted to `./context` in your compose file.

## Links

- [Agno Docs](https://docs.agno.com)
- [AgentOS Docs](https://docs.agno.com/agent-os/introduction)
