from agno.knowledge import Knowledge
from agno.tools import tool
from agno.tools.file import FileTools
from agno.tools.mcp import MCPTools
from agno.tools.sql import SQLTools

from db import PAL_SCHEMA, get_sql_engine
from pal.config import (
    EXA_MCP_URL,
    GOOGLE_INTEGRATION_ENABLED,
    PAL_CONTEXT_DIR,
    SLACK_TOKEN,
)


def create_update_knowledge(knowledge: Knowledge):
    """Create an update_knowledge tool bound to a specific knowledge base.

    The returned tool lets the agent save metadata (file manifests, schema
    index entries, source capabilities, discoveries) to the knowledge base.

    Args:
        knowledge: The Knowledge instance to insert into.

    Returns:
        A tool function that the agent can call.
    """

    @tool
    def update_knowledge(title: str, content: str) -> str:
        """Save metadata to the knowledge base.

        Use this to record structural information about Pal's context graph:
        - File manifests: what files exist and what they contain
        - Schema index: what SQL tables exist and their structure
        - Source capabilities: what tools are available
        - Discoveries: where information was found for specific topics

        Args:
            title: A descriptive title prefixed with its category
                (e.g. "Schema: pal_projects", "File: brand-voice.md",
                "Discovery: Project X", "Source: Gmail").
            content: The metadata content describing the resource —
                columns, purpose, location, tags, etc.

        Returns:
            Confirmation message.
        """
        knowledge.insert(name=title, text_content=content)
        return f"Knowledge updated: {title}"

    return update_knowledge


def build_tools(knowledge: Knowledge) -> list:
    tools: list = [
        SQLTools(db_engine=get_sql_engine(), schema=PAL_SCHEMA),
        FileTools(base_dir=PAL_CONTEXT_DIR, enable_delete_file=False),
        create_update_knowledge(knowledge),
        MCPTools(url=EXA_MCP_URL),
    ]

    if SLACK_TOKEN:
        from agno.tools.slack import SlackTools

        tools.append(
            SlackTools(
                enable_send_message=True,
                enable_list_channels=True,
                enable_send_message_thread=False,
                enable_get_channel_history=False,
                enable_upload_file=False,
                enable_download_file=False,
            )
        )

    if GOOGLE_INTEGRATION_ENABLED:
        from agno.tools.google.calendar import GoogleCalendarTools
        from agno.tools.google.gmail import GmailTools

        tools.append(GmailTools(send_email=False, send_email_reply=False, list_labels=True))
        tools.append(GoogleCalendarTools(allow_update=True))

    return tools
