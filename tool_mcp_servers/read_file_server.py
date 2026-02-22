"""MCP Server for read_file tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import read_file

mcp = FastMCP("read_file")


@mcp.tool()
def file_read(file_path: str) -> str:
    """Read and return the content of a file at a given path."""
    return read_file(file_path)


if __name__ == "__main__":
    mcp.run()
