"""MCP Server for generate_system_prompt builder tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from builder.builder_tools.generate_system_prompt import generate_system_prompt

import json

mcp = FastMCP("gen_system_prompt")


@mcp.tool()
def gen_system_prompt(user_instruction: str) -> str:
    """Analyze the user instruction and generate a full agent plan.
    Returns a JSON string. Parse it and use the fields as follows:
    - system_prompt (str): pass to gen_worker_agent and save_agent
    - goal (str): pass to gen_worker_agent, save_agent, and launch_agent
    - interval_hours (int): pass to gen_worker_agent, save_agent, and launch_agent
    - required_tools (LIST of strings): e.g. ["read_mail", "send_mail"]
      ALWAYS pass as a Python list to gen_worker_agent, save_agent, and launch_agent.
      NEVER convert to a string or JSON-encoded string.
    - missing_tools (list of dicts): each has 'name' and 'purpose' keys.
      If empty ([]), skip Step 2 entirely.
    """
    result = generate_system_prompt(user_instruction)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
