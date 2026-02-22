"""MCP Server for generate_system_prompt builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.generate_system_prompt import generate_system_prompt

import json

mcp = FastMCP("generate_system_prompt")


@mcp.tool()
def gen_system_prompt(user_instruction: str) -> str:
    """Generate system_prompt, goal, and interval_hours from a user instruction."""
    result = generate_system_prompt(user_instruction)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
