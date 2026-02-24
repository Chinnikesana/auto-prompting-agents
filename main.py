#!/usr/bin/env python3
"""
Dynamic Agent Creator — Main Entry Point

Modes:
  python main.py              → Interactive builder flow
  python main.py --list-agents → Show all created agents
  python main.py --list-tools  → Show all tools in registry
"""
import sys
import os
import argparse

from dotenv import load_dotenv
load_dotenv()


def print_banner():
    """Print the welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║            DYNAMIC AGENT CREATOR SYSTEM                 ║
║         Build AI Agents from Plain English              ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_mongo():
    """Verify MongoDB is reachable."""
    from db.mongo_client import check_connection
    if not check_connection():
        print("ERROR: Cannot connect to MongoDB!")
        print(f"   URI: {os.getenv('MONGO_URI', 'mongodb://localhost:27017/')}")
        print()
        print("   Please start MongoDB and try again:")
        print("   • Windows: net start MongoDB")
        print("   • Mac/Linux: mongod --dbdir /data/db")
        print("   • Docker: docker run -d -p 27017:27017 mongo")
        sys.exit(1)
    print("[OK] MongoDB connected")


def list_agents():
    """Print a table of all created agents."""
    from db.collections import agents
    docs = list(agents().find({}, {
        "_id": 0, "agent_id": 1, "status": 1, "last_run": 1,
        "agent_file": 1, "run_count": 1, "goal": 1,
    }).sort("agent_id", 1))

    if not docs:
        print("No agents created yet.")
        return

    print(f"\n{'ID':<12} {'Status':<10} {'Runs':<6} {'Last Run':<22} {'Goal'}")
    print("─" * 90)
    for d in docs:
        last = str(d.get("last_run", "never"))[:19] if d.get("last_run") else "never"
        goal = (d.get("goal", "")[:45] + "...") if len(d.get("goal", "")) > 45 else d.get("goal", "")
        print(f"{d.get('agent_id', '?'):<12} {d.get('status', '?'):<10} "
              f"{d.get('run_count', 0):<6} {last:<22} {goal}")
    print()


def list_tools():
    """Print all tools in the registry."""
    from tools_dir.registry import get_registry
    tools = get_registry()

    if not tools:
        print("No tools in registry.")
        return

    print(f"\n{'Name':<22} {'Type':<10} {'Status':<10} {'Description'}")
    print("─" * 90)
    for t in tools:
        kind = "custom" if t.get("is_custom") else "built-in"
        desc = (t.get("description", "")[:45] + "...") if len(t.get("description", "")) > 45 else t.get("description", "")
        print(f"{t['name']:<22} {kind:<10} {t.get('status', '?'):<10} {desc}")
    print()


def run_builder_flow():
    """Interactive builder flow — get user instruction, run the Builder, then launch the Worker."""
    from tools_dir.registry import load_registry
    from db.collections import ensure_indexes, agents

    # Setup
    ensure_indexes()
    registry = load_registry()
    print(f"Loaded {len(registry)} tools in registry\n")

    # Get user instruction
    print("Describe what you want your agent to do:")
    user_instruction = input(">>> ").strip()
    if not user_instruction:
        print("No instruction provided. Exiting.")
        sys.exit(0)

    print()

    # Run the Builder Agent (creates the worker agent file & saves to DB)
    from builder.builder_agent import start_builder
    start_builder(user_instruction)

    # After builder finishes, find the most recently created 'ready' agent
    agent_doc = agents().find_one(
        {"status": "ready"},
        sort=[("created_at", -1)],
    )

    if not agent_doc:
        print("\n[main] Builder finished. (No 'ready' agent found for auto-launch)")
        return

    agent_file = agent_doc.get("agent_file", "")
    agent_id = agent_doc.get("agent_id", "?")
    goal = agent_doc.get("goal", "...")

    if not agent_file or not os.path.isfile(agent_file):
        return

    print(f"\n{'='*60}")
    print(f" BUILD COMPLETE: {agent_id}")
    print(f" Goal: {goal}")
    print(f"{'='*60}")
    
    confirm = input(f"\nShall I launch your agent now? (y/n): ").strip().lower()
    if confirm != 'y':
        print(f"\n[main] Agent {agent_id} saved but not launched. You can run it manually:")
        print(f"       py {agent_file}")
        return

    print(f"\n[main] Launching worker agent {agent_id}...")
    
    # Update status to running
    agents().update_one(
        {"agent_id": agent_id},
        {"$set": {"status": "running"}},
    )

    # Launch in a CLEAN process to avoid event loop conflicts from the builder
    import subprocess
    import platform

    python_exe = sys.executable
    
    if platform.system() == "Windows":
        # Launch in a new terminal window on Windows for visibility
        subprocess.Popen(
            ["start", "cmd", "/k", python_exe, agent_file],
            shell=True
        )
    else:
        # Detached background process on Linux/Mac
        subprocess.Popen(
            [python_exe, agent_file],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    print(f"\n[main] Agent {agent_id} launched in a new process.")
    print(f"[main] You can check its progress in the new window or in the 'run_logs' database.")




def main():
    parser = argparse.ArgumentParser(description="Dynamic Agent Creator System")
    parser.add_argument("--list-agents", action="store_true",
                        help="List all created agents")
    parser.add_argument("--list-tools", action="store_true",
                        help="List all tools in registry")

    args = parser.parse_args()

    print_banner()
    check_mongo()

    if args.list_agents:
        list_agents()
    elif args.list_tools:
        list_tools()
    else:
        run_builder_flow()


if __name__ == "__main__":
    main()
