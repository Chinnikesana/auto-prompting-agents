"""
launch_worker_agent — Builder tool that starts the Worker Agent as a detached
subprocess and then terminates the Builder Agent.
"""
import sys
import platform
import subprocess
from db.collections import agents


def launch_worker_agent(agent_id: str, agent_file: str, goal: str,
                        tools: list[str], interval_hours: int) -> None:
    """
    Launch the Worker Agent as a detached subprocess and terminate the Builder.
    This is the final step — irreversible.
    """
    # Update agent status to running
    try:
        agents().update_one(
            {"agent_id": agent_id},
            {"$set": {"status": "running"}},
        )
    except Exception:
        pass

    # Print summary
    print("\n" + "=" * 60)
    print(f"  WORKER AGENT LAUNCH SUMMARY")
    print("=" * 60)
    print(f"  Agent ID:  {agent_id}")
    print(f"  File:      {agent_file}")
    print(f"  Goal:      {goal}")
    print(f"  Tools:     {', '.join(tools)}")
    print(f"  Interval:  {interval_hours}h {'(one-shot)' if interval_hours == 0 else '(repeating)'}")
    print("=" * 60 + "\n")

    # Launch as detached subprocess
    python_exe = sys.executable

    if platform.system() == "Windows":
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            [python_exe, agent_file],
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
    else:
        subprocess.Popen(
            [python_exe, agent_file],
            start_new_session=True,
            close_fds=True,
        )

    print(f"[Builder] Agent {agent_id} is now running. Builder Agent terminating.")
    sys.exit(0)
