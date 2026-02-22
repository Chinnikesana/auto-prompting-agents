"""
Tool Registry — in-memory list merged with MongoDB tool_registry on load.
Pre-built tools all live in tools_dir/builtin_tools.py (single file).
LLM-generated tools are individual files in tools_dir/.
"""
from db.collections import tool_registry as _db_collection

# Pre-built tools — all functions live in builtin_tools.py
_PREBUILT_TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web using DuckDuckGo and return top 5 results.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/web_search_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "web_scraper",
        "description": "Fetch a URL and extract clean text content from the page.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/web_scraper_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "datetime_tool",
        "description": "Return the current date and time as a formatted string.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/datetime_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "read_file",
        "description": "Read and return the content of a file at a given path.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/read_file_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "write_file",
        "description": "Write or append content to a file at a given path.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/write_file_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "http_request",
        "description": "Make an HTTP GET or POST request and return the response.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/http_request_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "read_email",
        "description": "Read recent emails from an IMAP mailbox.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/read_email_server.py",
        "status": "active",
        "is_custom": False,
    },
    {
        "name": "send_email",
        "description": "Send an email via SMTP using configured credentials.",
        "file_path": "tools_dir/builtin_tools.py",
        "mcp_server_path": "tool_mcp_servers/send_email_server.py",
        "status": "active",
        "is_custom": False,
    },
]

# In-memory merged registry
_registry: list[dict] = []


def load_registry() -> list[dict]:
    """Load pre-built tools and merge with custom tools from MongoDB."""
    global _registry
    _registry = list(_PREBUILT_TOOLS)

    existing_names = {t["name"] for t in _registry}

    try:
        custom_tools = _db_collection().find({"status": "active", "is_custom": True})
        for doc in custom_tools:
            if doc["name"] not in existing_names:
                _registry.append({
                    "name": doc["name"],
                    "description": doc.get("description", ""),
                    "file_path": doc.get("file_path", ""),
                    "mcp_server_path": doc.get("mcp_server_path", ""),
                    "status": "active",
                    "is_custom": True,
                })
                existing_names.add(doc["name"])
    except Exception:
        pass  # MongoDB may not be available; fallback to pre-built only

    return _registry


def get_registry() -> list[dict]:
    """Return the current registry (load if empty)."""
    if not _registry:
        load_registry()
    return _registry


def get_tool(name: str) -> dict | None:
    """Get a single tool by name."""
    for t in get_registry():
        if t["name"] == name:
            return t
    return None


def add_tool(tool: dict):
    """Add a tool to the in-memory registry."""
    existing = {t["name"] for t in _registry}
    if tool["name"] not in existing:
        _registry.append(tool)


def get_tool_list_string() -> str:
    """Return a compact string of tool names and descriptions for LLM prompts."""
    lines = []
    for t in get_registry():
        if t["status"] == "active":
            lines.append(f"{t['name']}: {t['description']}")
    return "\n".join(lines)
