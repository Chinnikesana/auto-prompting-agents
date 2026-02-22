"""MCP Server for launch_worker_agent builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.launch_worker_agent import launch_worker_agent

import json

mcp = FastMCP("launch_worker_agent")


@mcp.tool()
def launch_agent(agent_id: str, agent_file: str, goal: str,
                 tools: str, interval_hours: int) -> str:
    """Launch the Worker Agent as a detached subprocess. tools is a JSON array string."""
    tool_list = json.loads(tools) if isinstance(tools, str) else tools
    launch_worker_agent(agent_id, agent_file, goal, tool_list, interval_hours)
    return "Agent launched"  # This line won't be reached due to sys.exit


if __name__ == "__main__":
    mcp.run()
