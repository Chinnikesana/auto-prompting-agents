"""MCP Server for save_agent_to_db builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.save_agent_to_db import save_agent_to_db

import json

mcp = FastMCP("save_agent_to_db")


@mcp.tool()
def save_agent(agent_id: str, user_instruction: str, system_prompt: str,
               goal: str, tools: str, interval_hours: int,
               agent_file: str) -> str:
    """Save agent config to MongoDB. tools is a JSON array string."""
    tool_list = json.loads(tools) if isinstance(tools, str) else tools
    result = save_agent_to_db(agent_id, user_instruction, system_prompt,
                              goal, tool_list, interval_hours, agent_file)
    return result


if __name__ == "__main__":
    mcp.run()
