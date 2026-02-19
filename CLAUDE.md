# CLAUDE.md

This file provides context for Claude Code when working with this repository.

## Project Overview

Pal - A personal agent that learns your preferences, context, and history. Built with Agno.

## Architecture

```
AgentOS (app/main.py)
└── Pal (pal/agent.py)  # Personal agent with SQL + Exa MCP + LearningMachine
```

Pal uses:
- PostgreSQL database (pgvector) for persistence
- OpenAI GPT-5.2 model
- SQLTools for dynamic schema creation and queries
- Exa MCP for web research
- Dual knowledge system: `pal_knowledge` (RAG) + `pal_learnings` (LearningMachine)

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | AgentOS entry point, registers Pal agent |
| `app/config.yaml` | Quick prompts for Pal |
| `pal/agent.py` | Pal agent implementation |
| `db/session.py` | `get_postgres_db()` and `create_knowledge()` helpers |
| `db/url.py` | Builds database URL from environment |
| `compose.yaml` | Local development with Docker |

## Development Setup

### Virtual Environment

Use the venv setup script to create the development environment:

```bash
./scripts/venv_setup.sh
source .venv/bin/activate
```

### Format & Validation

Always run format and lint checks using the venv Python interpreter:

```bash
source .venv/bin/activate && ./scripts/format.sh
source .venv/bin/activate && ./scripts/validate.sh
```

## Conventions

### Agent Pattern

Pal follows the self-named package pattern (`pal/agent.py`):

```python
from agno.agent import Agent
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agno.models.openai import OpenAIResponses
from agno.tools.mcp import MCPTools
from agno.tools.sql import SQLTools
from db import create_knowledge, db_url, get_postgres_db

agent_db = get_postgres_db(contents_table="pal_contents")

pal_knowledge = create_knowledge("Pal Knowledge", "pal_knowledge")
pal_learnings = create_knowledge("Pal Learnings", "pal_learnings")

pal = Agent(
    id="pal",
    name="Pal",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    instructions=instructions,
    knowledge=pal_knowledge,
    search_knowledge=True,
    learning=LearningMachine(
        knowledge=pal_learnings,
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    ),
    tools=[
        SQLTools(db_url=db_url),
        MCPTools(url=EXA_MCP_URL),
    ],
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=10,
    markdown=True,
)
```

### Database

- Use `get_postgres_db()` from `db` module
- **Important**: The `contents_table` parameter is only needed when the database is provided to a Knowledge base as a `contents_db`. If your agent doesn't use a Knowledge base, just use `get_postgres_db()` without arguments.

```python
# Agent WITH a Knowledge base - use create_knowledge helper
from db import create_knowledge
knowledge = create_knowledge("My Knowledge", "my_vectors")

# Agent WITHOUT a Knowledge base - no contents_table needed
agent_db = get_postgres_db()
```

- Knowledge bases use PgVector with `SearchType.hybrid`
- Embeddings use `text-embedding-3-small`

### Imports

```python
# Database
from db import db_url, get_postgres_db, create_knowledge

# Agent
from pal.agent import pal
```

## Commands

```bash
# Setup virtual environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Local development with Docker
docker compose up -d --build

# Test Pal agent directly
python -m pal.agent

# Format & validation (run from activated venv)
./scripts/format.sh
./scripts/validate.sh
```

## Environment Variables

Required:
- `OPENAI_API_KEY`
- `EXA_API_KEY` - Exa MCP for web search

Optional:
- `DB_DRIVER` - Database driver (default: `postgresql+psycopg`)
- `PORT` - API server port (default: `8000`)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_DATABASE`
- `RUNTIME_ENV` - Set to `dev` for auto-reload

## Ports

- API: 8000
- Database: 5432

## Data Storage

| Data | Storage | Table/Location |
|------|---------|----------------|
| Pal knowledge (RAG) | PostgreSQL (vector embeddings) | `pal_knowledge` |
| Pal learnings (LearningMachine) | PostgreSQL (vector embeddings) | `pal_learnings` |
| Pal contents | PostgreSQL | `pal_contents` |
| User data (notes, people, etc.) | PostgreSQL (SQL) | `pal_*` tables (dynamic) |
| Sessions/memory | PostgreSQL | Automatic |

---

## Agno Framework Reference

### Model Providers

Agno supports 40+ model providers. Common options:

```python
# OpenAI (default in this project)
from agno.models.openai import OpenAIResponses
model = OpenAIResponses(id="gpt-5.2")

# Anthropic Claude
from agno.models.anthropic import Claude
model = Claude(id="claude-sonnet-4-5")

# Google Gemini
from agno.models.google import Gemini
model = Gemini(id="gemini-2.0-flash")

# Local models via Ollama
from agno.models.ollama import Ollama
model = Ollama(id="llama3")

# AWS Bedrock
from agno.models.aws import BedrockChat
model = BedrockChat(id="anthropic.claude-3-sonnet-20240229-v1:0")

# Azure OpenAI
from agno.models.azure import AzureOpenAI
model = AzureOpenAI(id="gpt-4", azure_endpoint="...", api_version="...")
```

### Knowledge & RAG

#### Search Types

```python
from agno.vectordb.pgvector import SearchType

SearchType.vector   # Semantic similarity search
SearchType.keyword  # Exact word/phrase matching
SearchType.hybrid   # Combined vector + keyword (recommended)
```

#### Knowledge Base Setup

```python
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

knowledge = Knowledge(
    name="My Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="my_vectors",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=get_postgres_db(contents_table="my_contents"),
    max_results=10,
)

# Load documents
knowledge.insert(name="Doc Name", url="https://example.com/doc.md")
knowledge.insert(name="Local File", path="/path/to/file.pdf")

# Use in agent
agent = Agent(
    knowledge=knowledge,
    search_knowledge=True,  # Enable automatic knowledge search
    ...
)
```

#### Supported Vector Databases

PgVector (used here), ChromaDB, LanceDB, Pinecone, Qdrant, Weaviate, Milvus, Redis, MongoDB, and 15+ others.

### Memory & Learning

#### Memory Types

- **User Memory**: Unstructured observations about users
- **User Profile**: Structured facts about users
- **Entity Memory**: Facts about companies, projects, people
- **Session Context**: Goals, plans, progress for active sessions

#### Learning Machines

For agents that learn and improve over time:

```python
from agno.learn import LearningMachine, LearningMode, LearnedKnowledgeConfig

agent = Agent(
    learning=LearningMachine(
        knowledge=my_knowledge_base,
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    ),
    ...
)
```

#### Simple Agentic Memory

For basic user preference tracking without a full knowledge base:

```python
agent = Agent(
    enable_agentic_memory=True,
    ...
)
```

### Tools

#### Built-in Tools

```python
# DuckDB for structured data
from agno.tools.duckdb import DuckDbTools
tools = [DuckDbTools(db_path="/data/my.db")]

# Web search
from agno.tools.duckduckgo import DuckDuckGoTools
tools = [DuckDuckGoTools()]

# File operations
from agno.tools.file import FileTools
tools = [FileTools()]

# Many more: Slack, Gmail, GitHub, Linear, etc.
# See: https://docs.agno.com/tools/toolkits
```

#### MCP Tools (Model Context Protocol)

Connect to external MCP servers:

```python
from agno.tools.mcp import MCPTools

# Remote MCP server
tools = [MCPTools(url="https://mcp.example.com/mcp")]

# Local MCP server (stdio)
tools = [MCPTools(command="npx @modelcontextprotocol/server-filesystem /path")]

# Multiple MCP servers
tools = [
    MCPTools(url="https://mcp.exa.ai/mcp?exaApiKey=..."),
    MCPTools(url="https://docs.agno.com/mcp"),
]
```

#### Custom Tools

```python
from agno.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """Search for something.

    Args:
        query: The search query.

    Returns:
        Search results as a string.
    """
    # Implementation
    return f"Results for: {query}"

agent = Agent(tools=[my_custom_tool], ...)
```

### Agent Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `id` | str | Unique identifier (used in config.yaml) |
| `name` | str | Display name |
| `model` | Model | Language model to use |
| `db` | PostgresDb | Database for persistence |
| `instructions` | str | System prompt |
| `tools` | list | Available tools |
| `knowledge` | Knowledge | Knowledge base for RAG |
| `search_knowledge` | bool | Auto-search knowledge base |
| `learning` | LearningMachine | Learning configuration |
| `enable_agentic_memory` | bool | Track user preferences |
| `add_datetime_to_context` | bool | Include current time |
| `add_history_to_context` | bool | Include chat history |
| `read_chat_history` | bool | Load previous messages |
| `num_history_runs` | int | Number of history runs to include |
| `markdown` | bool | Format responses as markdown |

### AgentOS Configuration

```python
from agno.os import AgentOS

agent_os = AgentOS(
    name="My AgentOS",
    agents=[agent1, agent2],
    teams=[team1],           # Optional: multi-agent teams
    workflows=[workflow1],   # Optional: sequential workflows
    knowledge=[kb1, kb2],    # Optional: shared knowledge bases
    db=get_postgres_db(),
    config="path/to/config.yaml",
    tracing=True,            # Enable distributed tracing
    enable_mcp_server=True,  # Expose as MCP server
)
```

### Hooks (Pre/Post Processing)

```python
from agno.os import AgentOS
from agno.os.hooks import hook

@hook
async def log_request(request):
    """Pre-execution hook."""
    print(f"Request: {request}")
    return request

@hook
async def log_response(response):
    """Post-execution hook."""
    print(f"Response: {response}")
    return response

agent_os = AgentOS(
    pre_hooks=[log_request],
    post_hooks=[log_response],
    run_hooks_in_background=True,  # Non-blocking execution
    ...
)
```

### Security

#### JWT Authentication

```python
from agno.os.security import JWTAuth

agent_os = AgentOS(
    auth=JWTAuth(
        secret="your-secret-key",
        algorithm="HS256",
    ),
    ...
)
```

#### RBAC Scopes

- `agents:read` - Read all agents
- `agents:<id>:run` - Run specific agent
- `agent_os:admin` - Full admin access

### Documentation Links

**LLM-friendly documentation (for fetching):**
- https://docs.agno.com/llms.txt - Concise overview of Agno framework
- https://docs.agno.com/llms-full.txt - Complete Agno documentation

**Web documentation:**
- [Agno Docs](https://docs.agno.com)
- [AgentOS Introduction](https://docs.agno.com/agent-os/introduction)
- [Tools & Integrations](https://docs.agno.com/tools/toolkits)
- [Model Providers](https://docs.agno.com/models)
- [Knowledge & RAG](https://docs.agno.com/knowledge)
- [MCP Integration](https://docs.agno.com/tools/mcp)
