"""PostToolUse hook: lint and type-check after every edit.

Runs ruff and mypy. If either fails, print its output to stderr and exit
non-zero. A tool that isn't installed is skipped with a note, not a failure.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys

FAILURE_EXIT_CODE = 2
# (module, arguments) run as `python -m <module> <arguments>`.
CHECKS = [
    ("ruff", ["check", "app", "tests"]),
    ("mypy", ["app"]),
]


def run_check(module: str, args: list[str]) -> str | None:
    """Run one tool; return its output if it failed, else None."""
    if importlib.util.find_spec(module) is None:
        print(f"Skipping {module}: not installed.", file=sys.stderr)
        return None
    result = subprocess.run(
        [sys.executable, "-m", module, *args], capture_output=True, text=True
    )
    if result.returncode == 0:
        return None
    return f"$ python -m {module} {' '.join(args)}\n{result.stdout}{result.stderr}"


def main() -> int:
    """Return 0 if every available check passes, else the failure exit code."""
    failures = [out for module, args in CHECKS if (out := run_check(module, args))]
    if not failures:
        return 0
    print("\n".join(failures), file=sys.stderr)
    return FAILURE_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
