"""
LLM-based grader for evaluating Pal responses.

Uses a small, fast model to evaluate if the agent's response correctly
handles the user's request given the expected behavior.
"""

from dataclasses import dataclass

from openai import OpenAI

from pal.paths import CONTEXT_DIR


@dataclass
class GradeResult:
    """Result of LLM grading."""

    passed: bool
    reasoning: str
    score: float  # 0.0 to 1.0


GRADER_SYSTEM_PROMPT = """\
You are evaluating a personal context-agent called Pal. Your job is to determine
if the agent's response correctly handles the user's request.

You will be given:
1. The user's question
2. The agent's response
3. Expected values that should appear in the answer
4. Quality criteria (if applicable)

Evaluate based on:
- Correctness: Does the response address the request appropriately?
- Completeness: Does it include the expected information?
- Tone: Does it match the expected voice/style (if quality criteria provided)?
- No hallucinations: The response should not include made-up information.

Be lenient about:
- Extra context or insights beyond what was asked
- Different phrasing or formatting
- Minor variations in wording

Respond in this exact format:
SCORE: [0.0-1.0]
PASSED: [true/false]
REASONING: [brief explanation]
"""


def grade_response(
    question: str,
    response: str,
    expected_values: list[str],
    quality_criteria: str | None = None,
    model: str = "gpt-5-mini",
) -> GradeResult:
    """Use an LLM to grade the agent's response."""
    client = OpenAI()

    expected_context = ""
    if expected_values:
        expected_context = f"Expected values to appear: {', '.join(expected_values)}"
    if quality_criteria:
        expected_context += f"\nQuality criteria: {quality_criteria}"

    user_message = f"""\
Question: {question}

Agent Response:
{response}

Expected Answer:
{expected_context}

Grade this response."""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": GRADER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=500,
    )

    grader_response = completion.choices[0].message.content or ""
    return _parse_grade_response(grader_response)


def grade_voice_adherence(
    question: str,
    response: str,
    voice_guide_name: str,
    quality_criteria: str,
    model: str = "gpt-5-mini",
) -> GradeResult:
    """Grade response against a voice guide loaded from the context directory."""
    # Determine voice guide path from question content
    voice_dir = CONTEXT_DIR / "voice"
    guide_path = voice_dir / voice_guide_name
    if guide_path.exists():
        voice_content = guide_path.read_text()
    else:
        voice_content = "(voice guide not found)"

    client = OpenAI()

    user_message = f"""\
Question: {question}

Agent Response:
{response}

Voice Guide Content:
{voice_content}

Quality Criteria:
{quality_criteria}

Grade how well the agent's response adheres to the voice guide and quality criteria."""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": GRADER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=500,
    )

    grader_response = completion.choices[0].message.content or ""
    return _parse_grade_response(grader_response)


def check_strings_in_response(response: str, expected: list[str]) -> list[str]:
    """Check which expected strings are missing from the response (case-insensitive)."""
    response_lower = response.lower()
    return [v for v in expected if v.lower() not in response_lower]


def _parse_grade_response(response: str) -> GradeResult:
    """Parse the grader's structured response into a GradeResult."""
    lines = response.strip().split("\n")

    score = 0.5
    passed = False
    reasoning = "Could not parse grader response"

    for line in lines:
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("PASSED:"):
            passed_str = line.split(":", 1)[1].strip().lower()
            passed = passed_str == "true"
        elif line.startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()

    return GradeResult(passed=passed, reasoning=reasoning, score=score)


def _infer_voice_guide(question: str) -> str:
    """Infer which voice guide file to use from the question text."""
    q = question.lower()
    if "x post" in q or "tweet" in q:
        return "x-post.md"
    if "linkedin" in q:
        return "linkedin-post.md"
    if "slack" in q:
        return "slack-message.md"
    if "email" in q:
        return "email.md"
    return "document.md"
