"""MCP Server for save_agent_to_db builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.save_agent_to_db import save_agent_to_db

import json

mcp = FastMCP("save_agent")


@mcp.tool()
def save_agent(agent_id: str, user_instruction: str, system_prompt: str,
               goal: str, tools: list, interval_hours: int,
               agent_file: str) -> str:
    """Save agent config to MongoDB.
    CRITICAL: agent_id and agent_file MUST be the exact values returned by gen_worker_agent.
    Do NOT invent or guess agent_id (e.g. '12345') or agent_file (e.g. 'agent.py').
    Use the agent_id and agent_file from the gen_worker_agent tool result only.
    tools must be a Python list of strings e.g. ["web_search", "send_email"].
    """
    tool_list = json.loads(tools) if isinstance(tools, str) else tools
    result = save_agent_to_db(agent_id, user_instruction, system_prompt,
                              goal, tool_list, interval_hours, agent_file)
    return result


if __name__ == "__main__":
    mcp.run()
