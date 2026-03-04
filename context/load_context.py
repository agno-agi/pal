#!/usr/bin/env python3
"""
Load context manifest into Pal's knowledge base.

Writes compact `File:` metadata entries into `pal_knowledge` for retrieval
routing. Does not ingest raw document contents — FileTools reads those on
demand from the context directory.

Usage:
    python context/load_context.py
    python context/load_context.py --recreate   # clear knowledge index and reload
    python context/load_context.py --dry-run    # preview without writing
"""

from argparse import ArgumentParser
from datetime import UTC, datetime
from os import getenv
from pathlib import Path

from db import create_knowledge
from pal.paths import CONTEXT_DIR

pal_knowledge = create_knowledge("Pal Knowledge", "pal_knowledge")

PAL_CONTEXT_DIR = Path(getenv("PAL_CONTEXT_DIR", str(CONTEXT_DIR)))

# File extensions treated as indexable context.
CONTEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json"}


def infer_intent_tags(path: Path, rel_path: str) -> list[str]:
    """Infer retrieval intent tags from file path and location.

    These are routing hints for the agent's recall step, not content indexes.
    Keep them broad — the agent reads the actual file when it needs detail.
    """
    name = path.name.lower()
    stem = path.stem.lower()
    parts = {p.lower() for p in rel_path.split("/")}
    tags: set[str] = set()

    # Location-based tags (check both dir components and file stem for flat files)
    if "voice" in parts:
        tags.update(["voice-guide", "content-generation"])
    if "preferences" in parts or stem == "preferences":
        tags.add("user-preferences")
    if "templates" in parts:
        tags.add("template")
    if "references" in parts:
        tags.add("reference")

    # Name-based tags
    if name in {"x-post.md", "linkedin-post.md"}:
        tags.add("social-post")
    if "email" in name:
        tags.add("email-draft")
    if "brief" in name or "project" in name:
        tags.add("project-context")
    if "meeting" in name:
        tags.add("meeting-notes")
    if "about-me" in name:
        tags.add("user-profile")
    if "slack" in name:
        tags.add("slack-message")
    if "document" in name:
        tags.add("long-form-writing")
    if "weekly" in name:
        tags.update(["weekly-review", "recurring"])

    return sorted(tags) if tags else ["general-context"]


def build_metadata_payload(path: Path, rel_path: str) -> str:
    """Build a compact metadata record for a knowledge map entry."""
    tags = infer_intent_tags(path, rel_path)
    size_kb = path.stat().st_size / 1024
    return (
        f"File: {rel_path} in context directory.\n"
        f"Size: {size_kb:.1f} KB\n"
        f"Intent tags: {', '.join(tags)}\n"
        f"Indexed: {datetime.now(UTC).isoformat()}\n"
    )


def discover_context_files(context_dir: Path) -> list[Path]:
    """Return all indexable context files, sorted by path."""
    if not context_dir.exists():
        return []
    return sorted(f for f in context_dir.rglob("*") if f.is_file() and f.suffix.lower() in CONTEXT_EXTENSIONS)


def clear_knowledge_index() -> None:
    """Clear the entire pal_knowledge vector store.

    Agno's PgVector doesn't support row-level deletes, so --recreate wipes
    all entries (File:, Schema:, Discovery:, Source:).  The agent will
    rebuild Schema:/Discovery:/Source: entries organically during use.
    """
    print("WARNING: Clearing entire pal_knowledge index (row-level delete not supported).")
    print("         Schema:, Discovery:, and Source: entries will be rebuilt during use.")
    pal_knowledge.vector_db.delete()


def load_context(*, recreate: bool = False, dry_run: bool = False) -> int:
    """Load context file metadata into pal_knowledge.

    Args:
        recreate: Clear entire knowledge index before loading.
        dry_run: Print what would be loaded without writing.

    Returns:
        Number of files loaded.
    """
    files = discover_context_files(PAL_CONTEXT_DIR)
    if not files:
        print(f"No context files found in {PAL_CONTEXT_DIR}")
        return 0

    if dry_run:
        print(f"Dry run — {len(files)} file(s) would be loaded:\n")
        for path in files:
            rel = str(path.relative_to(PAL_CONTEXT_DIR))
            tags = infer_intent_tags(path, rel)
            size_kb = path.stat().st_size / 1024
            print(f"  {rel}  ({size_kb:.1f} KB)  [{', '.join(tags)}]")
        return len(files)

    if recreate:
        clear_knowledge_index()

    loaded = 0
    for path in files:
        rel_path = str(path.relative_to(PAL_CONTEXT_DIR))
        text_content = build_metadata_payload(path=path, rel_path=rel_path)
        pal_knowledge.insert(
            name=f"File: {rel_path}",
            text_content=text_content,
            upsert=True,
        )
        print(f"  Loaded: {rel_path}")
        loaded += 1

    return loaded


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Load context file metadata into pal_knowledge.",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Clear entire knowledge index before loading.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files that would be loaded without writing.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    loaded = load_context(recreate=args.recreate, dry_run=args.dry_run)
    if not args.dry_run:
        print(f"\nLoaded {loaded} file(s) from {PAL_CONTEXT_DIR}")


if __name__ == "__main__":
    main()
