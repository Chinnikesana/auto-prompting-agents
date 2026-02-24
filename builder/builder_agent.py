"""
Builder Agent — the meta-agent that reads a user instruction and generates
a complete Worker Agent. Uses FastAgents with builder MCP servers.
LLM: Groq Cloud (llama-3.3-70b-versatile) — free, ~250 tok/sec.
"""
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

# Point FastAgents at Groq Cloud (OpenAI-compatible API)
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

import mcp_agent.core.fastagent as fast_agent

# Builder Agent system prompt — static and hardcoded
BUILDER_SYSTEM_PROMPT = """You are the Builder Agent. Execute this 5-step pipeline using tool calls only. No reasoning.

STEPS:
1. Call generate_system_prompt-gen_system_prompt(user_instruction) -> parse JSON, extract: system_prompt, goal, interval_hours, required_tools (list), missing_tools (list)
2. If missing_tools not empty: for each call create_new_tool-create_tool -> test_tool-run_test_tool -> register_tool-reg_tool. Append registered names to required_tools.
3. Call generate_worker_agent-gen_worker_agent(system_prompt, goal, tools, interval_hours, user_instruction) -> save returned agent_id and agent_file
4. Call save_agent_to_db-save_agent(agent_id, agent_file, system_prompt, goal, tools, interval_hours, user_instruction)
5. Call launch_worker_agent-launch_agent(agent_id, agent_file, goal, tools, interval_hours)

RULES (never break these):
- tools must be a Python list e.g. ["read_mail", "send_mail"] -- never a string
- agent_id and agent_file must be the EXACT values returned by generate_worker_agent-gen_worker_agent -- never invent them
- Execute steps in order, call tools immediately, do not think or reason"""

# Builder MCP servers
BUILDER_SERVERS = [
    "generate_system_prompt",
    "create_new_tool",
    "test_tool",
    "register_tool",
    "generate_worker_agent",
    "save_agent_to_db",
    "launch_worker_agent",
]

fast = fast_agent.FastAgent(
    name="builder_app", 
    config_path="fastagent.config.yaml",
    ignore_unknown_args=True
)


@fast.agent(
    name="builder",
    
    instruction=BUILDER_SYSTEM_PROMPT,
    servers=BUILDER_SERVERS,
    model="openai.meta-llama/llama-4-scout-17b-16e-instruct",  # Groq Cloud — better tool calling
)
async def builder_agent():
    pass


async def run_builder(user_instruction: str):
    """Run the Builder Agent with the given user instruction."""
    async with fast.run() as agent:
        await agent.builder.send(user_instruction)


def start_builder(user_instruction: str):
    """Synchronous entry point for the Builder Agent."""
    print("\n[Builder] Starting Builder Agent...")
    print(f"[Builder] User instruction: {user_instruction}")
    print("[Builder] LLM: Groq Cloud (llama-4-scout-17b-16e-instruct)")
    print("[Builder] Executing build pipeline...\n")

    asyncio.run(run_builder(user_instruction))
