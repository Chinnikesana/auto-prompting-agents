"""MCP Server for datetime_tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import datetime_tool

mcp = FastMCP("datetime_tool")


@mcp.tool()
def get_datetime() -> str:
    """Return the current date and time as a formatted string."""
    return datetime_tool()


if __name__ == "__main__":
    mcp.run()
