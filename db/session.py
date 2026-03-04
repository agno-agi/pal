"""
Database Session
----------------

PostgreSQL database connection for Pal.
"""

from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType
from sqlalchemy import Engine, create_engine, text

from db.url import db_url

DB_ID = "pal-db"

# PostgreSQL schema for user data tables (pal_notes, pal_people, etc.)
# Agno framework tables (sessions, knowledge vectors) stay in the default "ai" schema
PAL_SCHEMA = "pal"


def get_sql_engine() -> Engine:
    bootstrap = create_engine(db_url)
    with bootstrap.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {PAL_SCHEMA}"))
        conn.commit()
    bootstrap.dispose()
    return create_engine(
        db_url,
        connect_args={"options": f"-c search_path={PAL_SCHEMA},public"},
    )


def get_postgres_db(contents_table: str | None = None) -> PostgresDb:
    """Create a PostgresDb instance.

    Args:
        contents_table: Optional table name for storing knowledge contents.

    Returns:
        Configured PostgresDb instance.
    """
    if contents_table is not None:
        return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=contents_table)
    return PostgresDb(id=DB_ID, db_url=db_url)


def create_knowledge(name: str, table_name: str) -> Knowledge:
    """Create a Knowledge instance with PgVector hybrid search.

    Args:
        name: Display name for the knowledge base.
        table_name: PostgreSQL table name for vector storage.

    Returns:
        Configured Knowledge instance.
    """
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        contents_db=get_postgres_db(contents_table=f"{table_name}_contents"),
    )
