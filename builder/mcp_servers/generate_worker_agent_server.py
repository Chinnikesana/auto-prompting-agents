"""MCP Server for generate_worker_agent builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.generate_worker_agent import generate_worker_agent

import json

mcp = FastMCP("gen_worker_agent")


@mcp.tool()
def gen_worker_agent(system_prompt: str, goal: str, tools: list,
                     interval_hours: int, user_instruction: str) -> str:
    """Generate a standalone Worker Agent Python file. tools is a list of tool name strings e.g. [\"web_search\", \"send_email\"]."""
    tool_list = json.loads(tools) if isinstance(tools, str) else tools
    result = generate_worker_agent(system_prompt, goal, tool_list, interval_hours, user_instruction)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
