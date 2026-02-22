"""
generate_worker_agent — Builder tool that produces a complete standalone Worker Agent
Python file using an f-string template (no LLM call).
"""
import os
import datetime
from db.collections import agents


def generate_worker_agent(system_prompt: str, goal: str, tools: list[str],
                          interval_hours: int, user_instruction: str) -> dict:
    """
    Generate a standalone Worker Agent Python file.

    Returns:
        dict with keys: agent_id, agent_file
    """
    # Determine agent ID
    try:
        count = agents().count_documents({})
    except Exception:
        count = 0

    agent_id = f"agent_{count + 1:03d}"
    agent_file = os.path.join("generated_agents", f"{agent_id}.py")

    os.makedirs("generated_agents", exist_ok=True)

    # Build the MCP server names list for the tools
    tool_servers = ", ".join(f'"{t}"' for t in tools)
    timestamp = datetime.datetime.utcnow().isoformat()

    agent_code = f'''#!/usr/bin/env python3
"""
Worker Agent: {agent_id}
Created: {timestamp}
Original instruction: {user_instruction[:200]}
"""
import asyncio
import time
import sys
import os
import datetime

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB_NAME", "dynamic_agents")

_mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
_db = _mongo_client[MONGO_DB]

AGENT_ID = "{agent_id}"
SYSTEM_PROMPT = """{system_prompt}"""
GOAL = """{goal}"""
INTERVAL_HOURS = {interval_hours}
TOOLS = [{tool_servers}]

# --- Hugging Face Router Setup (OpenAI-compatible) ---
# FastAgents uses OpenAI SDK under the hood, so we point it at HF Router
os.environ["OPENAI_API_KEY"] = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN") or ""
os.environ["OPENAI_BASE_URL"] = "https://router.huggingface.co/v1"

# --- FastAgents Setup ---
import mcp_agent.core.fastagent as fast_agent

# Create the agent configuration
fast = fast_agent.FastAgent(name="worker_app")


@fast.agent(
    name="worker",
    instruction=SYSTEM_PROMPT,
    servers=TOOLS,
    model="openai.meta-llama/Llama-3.3-70B-Instruct",
)
async def worker_agent():
    pass


async def run_once():
    """Execute the agent task once and log the result."""
    started_at = datetime.datetime.utcnow()
    run_number = _db["agents"].find_one({{"agent_id": AGENT_ID}})
    current_count = run_number.get("run_count", 0) if run_number else 0

    try:
        async with fast.run() as agent:
            result = await agent.worker.send(GOAL)

        completed_at = datetime.datetime.utcnow()

        # Log the run
        _db["run_logs"].insert_one({{
            "agent_id": AGENT_ID,
            "run_number": current_count + 1,
            "started_at": started_at,
            "completed_at": completed_at,
            "goal": GOAL,
            "result": str(result)[:1000],
            "status": "success",
            "error": None,
        }})

        # Update agent record
        _db["agents"].update_one(
            {{"agent_id": AGENT_ID}},
            {{"$set": {{
                "last_run": completed_at,
                "status": "running",
            }}, "$inc": {{"run_count": 1}}}},
        )

        print(f"[{{AGENT_ID}}] Run {{current_count + 1}} completed successfully.")
        return result

    except Exception as e:
        completed_at = datetime.datetime.utcnow()
        _db["run_logs"].insert_one({{
            "agent_id": AGENT_ID,
            "run_number": current_count + 1,
            "started_at": started_at,
            "completed_at": completed_at,
            "goal": GOAL,
            "result": "",
            "status": "failed",
            "error": str(e)[:500],
        }})
        print(f"[{{AGENT_ID}}] Run {{current_count + 1}} failed: {{e}}")
        return None


def run_sync():
    """Synchronous wrapper for run_once."""
    return asyncio.run(run_once())


if __name__ == "__main__":
    print(f"[{{AGENT_ID}}] Starting Worker Agent...")
    print(f"  Model: Hugging Face Router (meta-llama/Llama-3.3-70B-Instruct)")
    print(f"  Goal: {{GOAL}}")
    print(f"  Tools: {{TOOLS}}")
    print(f"  Interval: {{INTERVAL_HOURS}} hours (0 = one-shot)")
    print()

    if INTERVAL_HOURS == 0:
        # One-shot execution
        run_sync()
        print(f"[{{AGENT_ID}}] One-shot execution complete. Exiting.")
    else:
        # Scheduled execution
        import schedule

        # Run immediately on start
        run_sync()

        # Schedule repeating runs
        schedule.every(INTERVAL_HOURS).hours.do(run_sync)
        print(f"[{{AGENT_ID}}] Scheduled to run every {{INTERVAL_HOURS}} hours. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print(f"\\n[{{AGENT_ID}}] Stopping...")
            _db["agents"].update_one(
                {{"agent_id": AGENT_ID}},
                {{"$set": {{"status": "stopped"}}}},
            )
            print(f"[{{AGENT_ID}}] Agent stopped cleanly.")
            sys.exit(0)
'''


    with open(agent_file, "w", encoding="utf-8") as f:
        f.write(agent_code)

    return {
        "agent_id": agent_id,
        "agent_file": agent_file,
    }
