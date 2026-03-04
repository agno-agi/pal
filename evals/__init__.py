"""
Evals Module
-------------

Evaluation suite for Pal. Demonstrates three eval types:

- **AccuracyEval**: Does the agent produce the correct answer?
- **AgentAsJudgeEval**: Is the response high-quality by LLM judgment?
- **ReliabilityEval**: Does the agent call the expected tools?

Run all evals:
    python -m evals
"""

from dataclasses import dataclass, field


@dataclass
class TestCase:
    """A test case for evaluating Pal."""

    question: str
    expected_strings: list[str]
    expected_tools: list[str]
    category: str
    exact_substring: str | None = None
    forbidden_strings: list[str] = field(default_factory=list)
    quality_criteria: str | None = None


CATEGORIES = [
    "fallback",
    "tool_routing",
    "capture",
    "retrieve",
    "file_ops",
    "voice_quality",
    "governance",
    "meta",
]

__all__ = [
    "CATEGORIES",
    "TestCase",
]
