"""Path constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PAL_DIR = Path(__file__).parent
CONTEXT_DIR = PROJECT_ROOT / "context"
VOICE_DIR = CONTEXT_DIR / "voice"

