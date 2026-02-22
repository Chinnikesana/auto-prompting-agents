"""MCP Server for web_search tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import web_search

mcp = FastMCP("web_search")


@mcp.tool()
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo and return top 5 results."""
    return web_search(query)


if __name__ == "__main__":
    mcp.run()
