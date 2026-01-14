"""
Entry point for running the MCP server as a module.

Usage:
    uv run python -m devvyn.mcp
    # or
    uv run --with mcp python -m devvyn.mcp
"""
from devvyn.mcp.server import main

if __name__ == "__main__":
    main()
