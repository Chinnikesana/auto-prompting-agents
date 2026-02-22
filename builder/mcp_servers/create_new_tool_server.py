"""MCP Server for create_new_tool builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.create_new_tool import create_new_tool

mcp = FastMCP("create_new_tool")


@mcp.tool()
def create_tool(tool_name: str, purpose: str, agent_id: str = "",
                attempt: int = 1, previous_error: str = "") -> str:
    """Write a new tool using the LLM. Returns the file path."""
    return create_new_tool(tool_name, purpose, agent_id, attempt, previous_error)


if __name__ == "__main__":
    mcp.run()
