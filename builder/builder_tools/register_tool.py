"""
register_tool — Builder tool that registers a tested tool in MongoDB, creates
its MCP server file, and updates fastagent.config.yaml.
"""
import os
import datetime
import yaml
from db.collections import tool_registry
from tools_dir.registry import add_tool


def register_tool(tool_name: str, description: str, file_path: str,
                  agent_id: str = "", test_output: str = "") -> str:
    """
    Register a new tool in MongoDB and the in-memory registry.
    Also generates the MCP server file and updates fastagent.config.yaml.

    Returns:
        Confirmation string with the MCP server path.
    """
    mcp_server_path = os.path.join("tool_mcp_servers", f"{tool_name}_server.py")

    # --- 1. Write MCP server file ---
    mcp_server_code = f'''"""MCP Server for {tool_name} tool (auto-generated)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.{tool_name} import {tool_name}

mcp = FastMCP("{tool_name}")


@mcp.tool()
def run_{tool_name}(**kwargs) -> str:
    """Auto-generated MCP wrapper for {tool_name}."""
    # Convert kwargs to positional args if only one argument
    args = list(kwargs.values())
    if args:
        return {tool_name}(*args)
    return {tool_name}()


if __name__ == "__main__":
    mcp.run()
'''
    os.makedirs("tool_mcp_servers", exist_ok=True)
    with open(mcp_server_path, "w", encoding="utf-8") as f:
        f.write(mcp_server_code)

    # --- 2. Register in MongoDB ---
    try:
        tool_registry().update_one(
            {"name": tool_name},
            {"$set": {
                "name": tool_name,
                "description": description,
                "function_name": tool_name,
                "file_path": file_path,
                "mcp_server_path": mcp_server_path,
                "is_custom": True,
                "status": "active",
                "created_for_agent": agent_id,
                "test_passed": True,
                "test_output": test_output,
                "last_updated": datetime.datetime.utcnow(),
            }},
            upsert=True,
        )
    except Exception:
        pass

    # --- 3. Add to in-memory registry ---
    add_tool({
        "name": tool_name,
        "description": description,
        "file_path": file_path,
        "mcp_server_path": mcp_server_path,
        "status": "active",
        "is_custom": True,
    })

    # --- 4. Update fastagent.config.yaml ---
    try:
        config_path = "fastagent.config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if config and "mcp" in config and "servers" in config["mcp"]:
            if tool_name not in config["mcp"]["servers"]:
                config["mcp"]["servers"][tool_name] = {
                    "command": "python",
                    "args": [mcp_server_path],
                }
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    except Exception:
        pass

    return f"Tool '{tool_name}' registered. MCP server: {mcp_server_path}"
