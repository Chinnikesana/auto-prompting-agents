"""
MongoDB collection accessors for the Dynamic Agent Creator system.
Collections: tool_registry, agents, run_logs, tool_creation_logs, llm_logs.
"""
from db.mongo_client import get_db


def tool_registry():
    """Tool registry — one document per tool."""
    return get_db()["tool_registry"]


def agents():
    """Agents — one document per generated Worker Agent."""
    return get_db()["agents"]


def run_logs():
    """Run logs — one document per Worker Agent execution."""
    return get_db()["run_logs"]


def tool_creation_logs():
    """Tool creation logs — one document per tool creation attempt."""
    return get_db()["tool_creation_logs"]


def llm_logs():
    """LLM logs — one document per LLM API call."""
    return get_db()["llm_logs"]


def ensure_indexes():
    """Create unique indexes on key collections."""
    tool_registry().create_index("name", unique=True, sparse=True)
    agents().create_index("agent_id", unique=True, sparse=True)
