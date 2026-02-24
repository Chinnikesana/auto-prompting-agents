"""
launch_worker_agent — Builder tool that marks the Worker Agent as ready
to launch. The actual execution happens in main.py after the builder exits.
"""
import json
from db.collections import agents


def launch_worker_agent(agent_id: str, agent_file: str, goal: str,
                        tools: list[str], interval_hours: int) -> str:
    """
    Mark the Worker Agent as ready to launch.
    Returns a JSON string with agent_id and agent_file so that main.py
    can pick it up and run it after the builder exits.
    """
    # Update agent status to "ready"
    try:
        agents().update_one(
            {"agent_id": agent_id},
            {"$set": {"status": "ready"}},
        )
    except Exception:
        pass

    # Print summary
    print("\n" + "=" * 60)
    print(f"  WORKER AGENT READY")
    print("=" * 60)
    print(f"  Agent ID:  {agent_id}")
    print(f"  File:      {agent_file}")
    print(f"  Goal:      {goal}")
    print(f"  Tools:     {', '.join(tools)}")
    print(f"  Interval:  {interval_hours}h {'(one-shot)' if interval_hours == 0 else '(repeating)'}")
    print("=" * 60 + "\n")

    return json.dumps({
        "agent_id": agent_id,
        "agent_file": agent_file,
        "status": "ready",
    })

