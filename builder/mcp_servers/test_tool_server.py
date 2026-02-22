"""MCP Server for test_tool builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.test_tool import test_tool

import json

mcp = FastMCP("test_tool")


@mcp.tool()
def run_test_tool(tool_name: str, file_path: str) -> str:
    """Test a tool in an isolated subprocess sandbox. Returns JSON with passed, output, error."""
    result = test_tool(tool_name, file_path)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
