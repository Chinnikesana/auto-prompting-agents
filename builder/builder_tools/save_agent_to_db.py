"""
save_agent_to_db — Builder tool that saves the full agent config to MongoDB.
"""
import datetime
from db.collections import agents


def save_agent_to_db(agent_id: str, user_instruction: str, system_prompt: str,
                     goal: str, tools: list[str], interval_hours: int,
                     agent_file: str) -> str:
    """
    Insert the complete agent configuration into MongoDB agents collection.

    Returns:
        The MongoDB _id of the inserted document as a string.
    """
    doc = {
        "agent_id": agent_id,
        "user_instruction": user_instruction,
        "system_prompt": system_prompt,
        "goal": goal,
        "tools": tools,
        "interval_hours": interval_hours,
        "agent_file": agent_file,
        "status": "starting",
        "created_at": datetime.datetime.utcnow(),
        "last_run": None,
        "run_count": 0,
    }

    result = agents().insert_one(doc)
    return str(result.inserted_id)
