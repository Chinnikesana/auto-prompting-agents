"""MCP Server for send_email tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import send_email

mcp = FastMCP("send_email")


@mcp.tool()
def email_send(to: str, subject: str, body: str) -> str:
    """Send an email via SMTP using configured credentials."""
    return send_email(to, subject, body)


if __name__ == "__main__":
    mcp.run()
