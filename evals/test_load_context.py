"""
Deterministic unit tests for context/load_context.py pure functions.

No agent, no API keys, no database needed. Runs standalone:
    python -m evals.test_load_context
"""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from context.load_context import (
    CONTEXT_EXTENSIONS,
    build_metadata_payload,
    discover_context_files,
    infer_intent_tags,
)
from pal.paths import CONTEXT_DIR

console = Console()


# ---------------------------------------------------------------------------
# infer_intent_tags tests
# ---------------------------------------------------------------------------


def test_voice_x_post_tags() -> None:
    path = Path("voice/x-post.md")
    tags = infer_intent_tags(path, "voice/x-post.md")
    assert "voice-guide" in tags, f"Expected 'voice-guide' in {tags}"
    assert "content-generation" in tags, f"Expected 'content-generation' in {tags}"
    assert "social-post" in tags, f"Expected 'social-post' in {tags}"


def test_voice_email_tags() -> None:
    path = Path("voice/email.md")
    tags = infer_intent_tags(path, "voice/email.md")
    assert "voice-guide" in tags, f"Expected 'voice-guide' in {tags}"
    assert "email-draft" in tags, f"Expected 'email-draft' in {tags}"


def test_preferences_tags() -> None:
    path = Path("preferences.md")
    tags = infer_intent_tags(path, "preferences.md")
    assert "user-preferences" in tags, f"Expected 'user-preferences' in {tags}"


def test_template_weekly_review_tags() -> None:
    path = Path("templates/weekly-review.md")
    tags = infer_intent_tags(path, "templates/weekly-review.md")
    assert "template" in tags, f"Expected 'template' in {tags}"
    assert "weekly-review" in tags, f"Expected 'weekly-review' in {tags}"
    assert "recurring" in tags, f"Expected 'recurring' in {tags}"


def test_meeting_notes_location_tag() -> None:
    path = Path("meetings/2026-03-03 - meeting - standup.md")
    tags = infer_intent_tags(path, "meetings/2026-03-03 - meeting - standup.md")
    assert "meeting-notes" in tags, f"Expected 'meeting-notes' in {tags}"


def test_project_location_tag() -> None:
    path = Path("projects/project - atlas.md")
    tags = infer_intent_tags(path, "projects/project - atlas.md")
    assert "project-context" in tags, f"Expected 'project-context' in {tags}"


def test_about_me_tags() -> None:
    path = Path("about-me.md")
    tags = infer_intent_tags(path, "about-me.md")
    assert "user-profile" in tags, f"Expected 'user-profile' in {tags}"


def test_slack_message_tags() -> None:
    path = Path("voice/slack-message.md")
    tags = infer_intent_tags(path, "voice/slack-message.md")
    assert "slack-message" in tags, f"Expected 'slack-message' in {tags}"
    assert "voice-guide" in tags, f"Expected 'voice-guide' in {tags}"


def test_document_voice_tags() -> None:
    path = Path("voice/document.md")
    tags = infer_intent_tags(path, "voice/document.md")
    assert "long-form-writing" in tags, f"Expected 'long-form-writing' in {tags}"
    assert "voice-guide" in tags, f"Expected 'voice-guide' in {tags}"


def test_fallback_general_context() -> None:
    path = Path("random-notes.md")
    tags = infer_intent_tags(path, "random-notes.md")
    assert tags == ["general-context"], f"Expected ['general-context'], got {tags}"


# ---------------------------------------------------------------------------
# discover_context_files tests
# ---------------------------------------------------------------------------


def test_discover_finds_known_files() -> None:
    files = discover_context_files(CONTEXT_DIR)
    names = {f.name for f in files}
    assert "about-me.md" in names, f"Expected about-me.md in {names}"
    assert "preferences.md" in names, f"Expected preferences.md in {names}"
    # Voice directory
    assert "x-post.md" in names, f"Expected x-post.md in {names}"
    # Templates directory
    assert "meeting-notes.md" in names, f"Expected meeting-notes.md in {names}"


def test_discover_only_valid_extensions() -> None:
    files = discover_context_files(CONTEXT_DIR)
    for f in files:
        assert f.suffix.lower() in CONTEXT_EXTENSIONS, f"Unexpected extension: {f.suffix} in {f}"


# ---------------------------------------------------------------------------
# build_metadata_payload tests
# ---------------------------------------------------------------------------


def test_build_metadata_payload_structure() -> None:
    # Use a real file so stat() works
    real_file = CONTEXT_DIR / "about-me.md"
    payload = build_metadata_payload(real_file, "about-me.md")
    assert "File:" in payload, "Expected 'File:' in payload"
    assert "Intent tags:" in payload, "Expected 'Intent tags:' in payload"
    assert "Size:" in payload, "Expected 'Size:' in payload"
    assert "Indexed:" in payload, "Expected 'Indexed:' in payload"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    test_voice_x_post_tags,
    test_voice_email_tags,
    test_preferences_tags,
    test_template_weekly_review_tags,
    test_meeting_notes_location_tag,
    test_project_location_tag,
    test_about_me_tags,
    test_slack_message_tags,
    test_document_voice_tags,
    test_fallback_general_context,
    test_discover_finds_known_files,
    test_discover_only_valid_extensions,
    test_build_metadata_payload_structure,
]


def run_unit_tests() -> bool:
    """Run all unit tests and print results. Returns True if all passed."""
    console.print(Panel("[bold]Unit Tests: context/load_context.py[/bold]", style="blue"))

    passed = 0
    failed = 0
    errors: list[tuple[str, str]] = []

    for test_fn in ALL_TESTS:
        name = test_fn.__name__
        try:
            test_fn()
            console.print(f"  [green]PASS[/green]  {name}")
            passed += 1
        except AssertionError as e:
            console.print(f"  [red]FAIL[/red]  {name}: {e}")
            errors.append((name, str(e)))
            failed += 1
        except Exception as e:
            console.print(f"  [yellow]ERR [/yellow]  {name}: {e}")
            errors.append((name, str(e)))
            failed += 1

    total = passed + failed
    rate = (passed / total * 100) if total else 0
    style = "green" if failed == 0 else "red"
    console.print(
        Panel(
            Text(f"{passed}/{total} passed ({rate:.0f}%)", style=style),
            title="[bold]Unit Test Summary[/bold]",
            border_style=style,
        )
    )
    return failed == 0


if __name__ == "__main__":
    import sys

    success = run_unit_tests()
    sys.exit(0 if success else 1)
