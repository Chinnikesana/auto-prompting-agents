"""MCP Server for http_request tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import http_request

import json

mcp = FastMCP("http_request")


@mcp.tool()
def make_http_request(url: str, method: str = "GET", headers: str = "", body: str = "") -> str:
    """Make an HTTP GET or POST request and return the response."""
    h = json.loads(headers) if headers else None
    b = json.loads(body) if body else None
    return http_request(url, method, h, b)


if __name__ == "__main__":
    mcp.run()
