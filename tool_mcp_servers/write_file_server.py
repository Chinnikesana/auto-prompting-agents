"""MCP Server for write_file tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import write_file

mcp = FastMCP("write_file")


@mcp.tool()
def file_write(file_path: str, content: str, mode: str = "write") -> str:
    """Write or append content to a file at a given path."""
    return write_file(file_path, content, mode)


if __name__ == "__main__":
    mcp.run()
