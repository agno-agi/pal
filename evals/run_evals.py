"""
Run evaluations against Pal.

Usage:
    python -m evals.run_evals
    python -m evals.run_evals --category fallback
    python -m evals.run_evals --verbose
    python -m evals.run_evals --llm-grader
"""

import argparse
import time
from typing import TypedDict

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text

from evals import CATEGORIES, TestCase
from evals.grader import check_strings_in_response
from evals.test_cases import TEST_CASES


class EvalResult(TypedDict, total=False):
    status: str
    question: str
    category: str
    missing: list[str] | None
    forbidden_found: list[str] | None
    tools_missing: list[str] | None
    duration: float
    response: str | None
    error: str
    llm_grade: float | None
    llm_reasoning: str | None


console = Console()


def evaluate_response(
    test_case: TestCase,
    response: str,
    tool_calls: list[str],
    llm_grader: bool = False,
) -> dict:
    """Evaluate an agent response using configured methods.

    Priority for final status:
    exact_substring fail > forbidden violation > tool failure > string match fail > LLM grade
    """
    result: dict = {}

    # 1. Exact substring check (deterministic)
    exact_pass: bool | None = None
    if test_case.exact_substring:
        exact_pass = test_case.exact_substring in response
        if not exact_pass:
            result["status"] = "FAIL"
            result["missing"] = [f"exact: {test_case.exact_substring[:60]}..."]
            return result

    # 2. Forbidden strings check (deterministic)
    forbidden_found: list[str] = []
    if test_case.forbidden_strings:
        response_lower = response.lower()
        forbidden_found = [f for f in test_case.forbidden_strings if f.lower() in response_lower]
        result["forbidden_found"] = forbidden_found if forbidden_found else None
        if forbidden_found:
            result["status"] = "FAIL"
            result["missing"] = [f"forbidden: {', '.join(forbidden_found)}"]
            return result

    # 3. Tool call verification (ReliabilityEval)
    tools_pass: bool | None = None
    if test_case.expected_tools:
        tools_missing = [t for t in test_case.expected_tools if t not in tool_calls]
        result["tools_missing"] = tools_missing if tools_missing else None
        tools_pass = len(tools_missing) == 0
        if not tools_pass:
            result["status"] = "FAIL"
            result["missing"] = [f"tools: {', '.join(tools_missing)}"]
            return result

    # 4. String matching (AccuracyEval)
    string_pass = True
    if test_case.expected_strings:
        missing = check_strings_in_response(response, test_case.expected_strings)
        result["missing"] = missing if missing else None
        string_pass = len(missing) == 0
        if not string_pass:
            result["status"] = "FAIL"
            return result

    # 5. LLM grading (AgentAsJudgeEval) — only if enabled and quality_criteria set
    llm_pass: bool | None = None
    if llm_grader and test_case.quality_criteria:
        try:
            from evals.grader import _infer_voice_guide, grade_voice_adherence

            voice_guide = _infer_voice_guide(test_case.question)
            grade = grade_voice_adherence(
                question=test_case.question,
                response=response,
                voice_guide_name=voice_guide,
                quality_criteria=test_case.quality_criteria,
            )
            result["llm_grade"] = grade.score
            result["llm_reasoning"] = grade.reasoning
            llm_pass = grade.passed
        except Exception as e:
            result["llm_grade"] = None
            result["llm_reasoning"] = f"Error: {e}"

    # Determine final status
    if llm_pass is not None:
        result["status"] = "PASS" if llm_pass else "FAIL"
    else:
        result["status"] = "PASS"

    return result


def _extract_tool_calls(run_result: object) -> list[str]:
    """Extract tool call names from an Agno RunResponse."""
    tool_names: list[str] = []
    messages = getattr(run_result, "messages", None) or []
    for msg in messages:
        if msg.get("role") == "assistant":
            for tc in msg.get("tool_calls", []):
                fn = tc.get("function", {})
                name = fn.get("name", "")
                if name:
                    tool_names.append(name)
    return tool_names


def run_evals(
    category: str | None = None,
    verbose: bool = False,
    llm_grader: bool = False,
) -> None:
    """Run evaluation suite."""
    from pal.agent import pal

    tests = TEST_CASES
    if category:
        tests = [tc for tc in tests if tc.category == category]

    if not tests:
        console.print(f"[red]No tests found for category: {category}[/red]")
        return

    mode_info = []
    if llm_grader:
        mode_info.append("LLM grading")
    if not mode_info:
        mode_info.append("String matching + tool verification")

    console.print(
        Panel(
            f"[bold]Running {len(tests)} tests[/bold]\nMode: {', '.join(mode_info)}",
            style="blue",
        )
    )

    results: list[EvalResult] = []
    start = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Evaluating...", total=len(tests))

        for test_case in tests:
            progress.update(task, description=f"[cyan]{test_case.question[:40]}...[/cyan]")
            test_start = time.time()

            try:
                run_result = pal.run(test_case.question)
                response = run_result.content or ""
                tool_calls = _extract_tool_calls(run_result)
                duration = time.time() - test_start

                eval_result = evaluate_response(
                    test_case=test_case,
                    response=response,
                    tool_calls=tool_calls,
                    llm_grader=llm_grader,
                )

                results.append(
                    {
                        "status": eval_result["status"],
                        "question": test_case.question,
                        "category": test_case.category,
                        "missing": eval_result.get("missing"),
                        "duration": duration,
                        "response": response if verbose else None,
                        "llm_grade": eval_result.get("llm_grade"),
                        "llm_reasoning": eval_result.get("llm_reasoning"),
                    }
                )

            except Exception as e:
                duration = time.time() - test_start
                results.append(
                    {
                        "status": "ERROR",
                        "question": test_case.question,
                        "category": test_case.category,
                        "missing": None,
                        "duration": duration,
                        "error": str(e),
                        "response": None,
                    }
                )

            progress.advance(task)

    total_duration = time.time() - start
    display_results(results, verbose, llm_grader)
    display_summary(results, total_duration, category)


def display_results(results: list[EvalResult], verbose: bool, llm_grader: bool) -> None:
    """Display results table."""
    table = Table(title="Results", show_lines=True)
    table.add_column("Status", style="bold", width=6)
    table.add_column("Category", style="dim", width=14)
    table.add_column("Question", width=45)
    table.add_column("Time", justify="right", width=6)
    table.add_column("Notes", width=35)

    for r in results:
        if r["status"] == "PASS":
            status = Text("PASS", style="green")
            notes = ""
            if llm_grader and r.get("llm_grade") is not None:
                notes = f"LLM: {r['llm_grade']:.1f}"
        elif r["status"] == "FAIL":
            status = Text("FAIL", style="red")
            llm_reasoning = r.get("llm_reasoning")
            missing = r.get("missing")
            if llm_grader and llm_reasoning:
                notes = llm_reasoning[:35]
            elif missing:
                notes = f"Missing: {', '.join(missing[:2])}"
            else:
                notes = ""
        else:
            status = Text("ERR", style="yellow")
            notes = (r.get("error") or "")[:35]

        table.add_row(
            status,
            r["category"],
            r["question"][:43] + "..." if len(r["question"]) > 43 else r["question"],
            f"{r['duration']:.1f}s",
            notes,
        )

    console.print(table)

    if verbose:
        failures = [r for r in results if r["status"] == "FAIL" and r.get("response")]
        if failures:
            console.print("\n[bold red]Failed Responses:[/bold red]")
            for r in failures:
                resp = r["response"] or ""
                panel_content = resp[:500] + "..." if len(resp) > 500 else resp
                if r.get("llm_reasoning"):
                    panel_content += f"\n\n[dim]LLM Reasoning: {r['llm_reasoning']}[/dim]"
                console.print(
                    Panel(
                        panel_content,
                        title=f"[red]{r['question'][:60]}[/red]",
                        border_style="red",
                    )
                )


def display_summary(results: list[EvalResult], total_duration: float, category: str | None) -> None:
    """Display summary statistics."""
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    total = len(results)
    rate = (passed / total * 100) if total else 0

    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column()

    summary.add_row("Total:", f"{total} tests in {total_duration:.1f}s")
    summary.add_row("Passed:", Text(f"{passed} ({rate:.0f}%)", style="green"))
    summary.add_row("Failed:", Text(str(failed), style="red" if failed else "dim"))
    summary.add_row("Errors:", Text(str(errors), style="yellow" if errors else "dim"))
    summary.add_row("Avg time:", f"{total_duration / total:.1f}s per test" if total else "N/A")

    llm_grades: list[float] = [
        r["llm_grade"] for r in results if r.get("llm_grade") is not None and isinstance(r["llm_grade"], (int, float))
    ]
    if llm_grades:
        avg_grade = sum(llm_grades) / len(llm_grades)
        summary.add_row("Avg LLM Score:", f"{avg_grade:.2f}")

    console.print(
        Panel(
            summary,
            title="[bold]Summary[/bold]",
            border_style="green" if rate == 100 else "yellow",
        )
    )

    if not category and len(CATEGORIES) > 1:
        cat_table = Table(title="By Category", show_header=True)
        cat_table.add_column("Category")
        cat_table.add_column("Passed", justify="right")
        cat_table.add_column("Total", justify="right")
        cat_table.add_column("Rate", justify="right")

        for cat in CATEGORIES:
            cat_results = [r for r in results if r["category"] == cat]
            if not cat_results:
                continue
            cat_passed = sum(1 for r in cat_results if r["status"] == "PASS")
            cat_total = len(cat_results)
            cat_rate = (cat_passed / cat_total * 100) if cat_total else 0

            rate_style = "green" if cat_rate == 100 else "yellow" if cat_rate >= 50 else "red"
            cat_table.add_row(
                cat,
                str(cat_passed),
                str(cat_total),
                Text(f"{cat_rate:.0f}%", style=rate_style),
            )

        console.print(cat_table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Pal evaluations")
    parser.add_argument("--category", "-c", choices=CATEGORIES, help="Filter by category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full responses on failure")
    parser.add_argument(
        "--llm-grader",
        "-g",
        action="store_true",
        help="Use LLM to grade voice_quality responses (requires OPENAI_API_KEY)",
    )
    args = parser.parse_args()

    run_evals(
        category=args.category,
        verbose=args.verbose,
        llm_grader=args.llm_grader,
    )
