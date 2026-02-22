"""MCP Server for read_email tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import read_email

mcp = FastMCP("read_email")


@mcp.tool()
def email_read(count: int = 5, folder: str = "INBOX") -> str:
    """Read recent emails from the configured IMAP mailbox."""
    return read_email(count, folder)


if __name__ == "__main__":
    mcp.run()
