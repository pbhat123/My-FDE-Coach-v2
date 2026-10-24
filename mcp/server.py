"""MCP server exposing the study guides in resources/.

Run it:
    python mcp/server.py
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"
GUIDE_SUFFIX = ".md"

mcp = FastMCP("interview-guides")


def guide_names() -> list[str]:
    """Return the guide names (file names without .md), sorted."""
    return sorted(path.stem for path in RESOURCES_DIR.glob(f"*{GUIDE_SUFFIX}"))


@mcp.tool
def list_guides() -> list[str]:
    """List the available study guides."""
    return guide_names()


@mcp.tool
def get_guide(name: str) -> str:
    """Return the full markdown of one study guide, e.g. 'decomposition-guide'."""
    # Checking against the known names also blocks paths like '../.env'.
    if name not in guide_names():
        available = ", ".join(guide_names())
        raise ToolError(f"No guide named '{name}'. Available guides: {available}")
    return (RESOURCES_DIR / f"{name}{GUIDE_SUFFIX}").read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
