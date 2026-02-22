"""MCP Server for register_tool builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.register_tool import register_tool

mcp = FastMCP("register_tool")


@mcp.tool()
def reg_tool(tool_name: str, description: str, file_path: str,
             agent_id: str = "", test_output: str = "") -> str:
    """Register a tested tool in MongoDB, create MCP server, update config."""
    return register_tool(tool_name, description, file_path, agent_id, test_output)


if __name__ == "__main__":
    mcp.run()
