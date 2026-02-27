"""MCP Server for text_to_speech tool (auto-generated)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.text_to_speech import text_to_speech

mcp = FastMCP("text_to_speech")


@mcp.tool()
def run_text_to_speech(**kwargs) -> str:
    """Auto-generated MCP wrapper for text_to_speech."""
    # Convert kwargs to positional args if only one argument
    args = list(kwargs.values())
    if args:
        return text_to_speech(*args)
    return text_to_speech()


if __name__ == "__main__":
    mcp.run()
