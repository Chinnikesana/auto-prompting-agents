"""MCP Server for web_scraper tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from tools_dir.builtin_tools import web_scraper

mcp = FastMCP("web_scraper")


@mcp.tool()
def scrape_web(url: str) -> str:
    """Fetch a URL and extract clean text content from the page."""
    return web_scraper(url)


if __name__ == "__main__":
    mcp.run()
