"""PreToolUse hook: block Claude from reading .env files.

Reads the tool-call JSON from stdin. If the file path contains ".env" (but not
".env.example"), print a reason to stderr and exit 2, which blocks the call.
"""
from __future__ import annotations

import json
import sys

BLOCK_EXIT_CODE = 2
SECRET_MARKER = ".env"
ALLOWED_MARKER = ".env.example"


def is_blocked(path: str) -> bool:
    """Return True if the path points at a secrets file."""
    return SECRET_MARKER in path and ALLOWED_MARKER not in path


def main() -> int:
    """Return the hook's exit code for the tool call on stdin."""
    call = json.load(sys.stdin)
    path = call.get("tool_input", {}).get("file_path", "")
    if not is_blocked(path):
        return 0
    print(
        f"Blocked: reading '{path}' is not allowed. "
        "Never read .env or API keys; use .env.example instead.",
        file=sys.stderr,
    )
    return BLOCK_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
