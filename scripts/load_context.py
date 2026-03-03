#!/usr/bin/env python3
"""
Load files from the context directory into Pal's knowledge base.
"""

from argparse import ArgumentParser
from pathlib import Path

from pal.agent import pal_knowledge
from pal.paths import CONTEXT_DIR


def discover_context_files(context_dir: Path) -> list[Path]:
    """Return context files grouped by top-level directories."""
    if not context_dir.exists():
        return []

    context_files: list[Path] = []
    for subdir in sorted(context_dir.iterdir()):
        if not subdir.is_dir():
            continue
        context_files.extend(sorted(file for file in subdir.rglob("*.md") if file.is_file()))
    return context_files


def load_context(*, recreate: bool = False) -> int:
    """Load context files into `pal_knowledge`.

    Args:
        recreate: If True, clear existing knowledge first.

    Returns:
        Number of files loaded.
    """
    files = discover_context_files(CONTEXT_DIR)
    if not files:
        print(f"No context files found in {CONTEXT_DIR}")
        return 0

    if recreate:
        try:
            print("Recreate requested — clearing context knowledge index.")
            pal_knowledge.vector_db.delete()
            print("Context knowledge index cleared.")
        except Exception as exc:
            raise RuntimeError(
                "Failed to clear context knowledge. Ensure the Pal knowledge tables exist."
            ) from exc

    for path in files:
        rel_path = str(path.relative_to(CONTEXT_DIR))
        pal_knowledge.insert(name=rel_path, path=str(path), upsert=True)
        print(f"Loaded: {rel_path}")

    return len(files)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Load context files into pal_knowledge.")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Drop and reload context knowledge index.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    loaded = load_context(recreate=args.recreate)
    print(f"Loaded {loaded} file(s) from {CONTEXT_DIR}")


if __name__ == "__main__":
    main()

