"""
Run all Pal evals.

Usage:
    python -m evals                # unit tests + agent evals
    python -m evals --unit-only    # unit tests only
"""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Pal evals")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests, skip agent evals")
    parser.add_argument("--category", "-c", help="Filter agent evals by category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full responses on failure")
    parser.add_argument("--llm-grader", "-g", action="store_true", help="Enable LLM grading for voice_quality")
    args = parser.parse_args()

    from evals.test_load_context import run_unit_tests

    unit_passed = run_unit_tests()

    if args.unit_only:
        sys.exit(0 if unit_passed else 1)

    from evals.run_evals import run_evals

    run_evals(
        category=args.category,
        verbose=args.verbose,
        llm_grader=args.llm_grader,
    )


if __name__ == "__main__":
    main()
