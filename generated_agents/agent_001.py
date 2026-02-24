#!/usr/bin/env python3
"""
Worker Agent: agent_001
Created: 2026-02-24T06:06:46.596042
Original instruction: look for latest web developer job posts and send the list to my n200626@rguktn.ac.in
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

AGENT_ID = "agent_001"
SYSTEM_PROMPT = """You are an AI agent that searches for the latest web developer job postings and sends them to a specified email address."""
GOAL = """Find the latest web developer job posts and send the list to n200626@rguktn.ac.in."""
INTERVAL_HOURS = 0
TOOLS = ["web_search", "send_email"]

# --- Groq Cloud Setup (OpenAI-compatible, free tier, ~250 tok/sec) ---
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

# --- FastAgents Setup ---
import mcp_agent.core.fastagent as fast_agent

# Create the agent configuration
fast = fast_agent.FastAgent(name="worker_app", config_path="fastagent.config.yaml", ignore_unknown_args=True)


@fast.agent(
    name="worker",
    instruction=SYSTEM_PROMPT,
    servers=TOOLS,
    model="openai.llama-3.3-70b-versatile",  # Groq Cloud
)
async def worker_agent():
    pass


async def run_once():
    """Execute the agent task once and log the result."""
    started_at = datetime.datetime.utcnow()
    run_number = _db["agents"].find_one({"agent_id": AGENT_ID})
    current_count = run_number.get("run_count", 0) if run_number else 0

    try:
        async with fast.run() as agent:
            result = await agent.worker.send(GOAL)

        completed_at = datetime.datetime.utcnow()

        # Log the run
        _db["run_logs"].insert_one({
            "agent_id": AGENT_ID,
            "run_number": current_count + 1,
            "started_at": started_at,
            "completed_at": completed_at,
            "goal": GOAL,
            "result": str(result)[:1000],
            "status": "success",
            "error": None,
        })

        # Update agent record
        _db["agents"].update_one(
            {"agent_id": AGENT_ID},
            {"$set": {
                "last_run": completed_at,
                "status": "running",
            }, "$inc": {"run_count": 1}},
        )

        print(f"[{AGENT_ID}] Run {current_count + 1} completed successfully.")
        return result

    except Exception as e:
        completed_at = datetime.datetime.utcnow()
        _db["run_logs"].insert_one({
            "agent_id": AGENT_ID,
            "run_number": current_count + 1,
            "started_at": started_at,
            "completed_at": completed_at,
            "goal": GOAL,
            "result": "",
            "status": "failed",
            "error": str(e)[:500],
        })
        print(f"[{AGENT_ID}] Run {current_count + 1} failed: {e}")
        return None


def run_sync():
    """Synchronous wrapper for run_once."""
    return asyncio.run(run_once())


if __name__ == "__main__":
    print(f"[{AGENT_ID}] Starting Worker Agent...")
    print(f"  Model   : ollama / qwen3:8b (local)")
    print(f"  Goal    : {GOAL}")
    print(f"  Tools   : {TOOLS}")
    print(f"  Interval: {INTERVAL_HOURS} hours (0 = one-shot)")
    print(f"  System prompt preview: {SYSTEM_PROMPT[:120]}...")
    print()

    if INTERVAL_HOURS == 0:
        # One-shot execution
        run_sync()
        print(f"[{AGENT_ID}] One-shot execution complete. Exiting.")
    else:
        # Scheduled execution
        import schedule

        # Run immediately on start
        run_sync()

        # Schedule repeating runs
        schedule.every(INTERVAL_HOURS).hours.do(run_sync)
        print(f"[{AGENT_ID}] Scheduled to run every {INTERVAL_HOURS} hours. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print(f"\n[{AGENT_ID}] Stopping...")
            _db["agents"].update_one(
                {"agent_id": AGENT_ID},
                {"$set": {"status": "stopped"}},
            )
            print(f"[{AGENT_ID}] Agent stopped cleanly.")
            sys.exit(0)
