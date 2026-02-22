"""
Builder Agent — the meta-agent that reads a user instruction and generates
a complete Worker Agent. Uses FastAgents with 8 builder MCP servers.
All LLM calls use free models via OpenRouter.
"""
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

# Point FastAgents at Hugging Face Router (OpenAI-compatible)
os.environ["OPENAI_API_KEY"] = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN") or ""
os.environ["OPENAI_BASE_URL"] = "https://router.huggingface.co/v1"

import mcp_agent.core.fastagent as fast_agent

# Builder Agent system prompt — static and hardcoded
BUILDER_SYSTEM_PROMPT = """You are the Builder Agent. Your job is to set up a new AI Worker Agent from a user instruction. 

Follow this streamlined pipeline:

Step 1: Call generate_system_prompt. This returns a full plan: system_prompt, goal, interval_hours, required_tools, and missing_tools.
Step 2: If "missing_tools" is NOT empty:
  - For each missing tool: call create_new_tool with its name and purpose.
  - Call test_tool with the tool path.
  - If test passes: call register_tool. 
  - If test fails: retry create_new_tool once with the error, then skip if it fails again.
Step 3: Call generate_worker_agent with the complete config (including both required_tools and newly registered tools).
Step 4: Call save_agent_to_db with the config and agent file path.
Step 5: Call launch_worker_agent. This will terminate you.

Be methodical. Use the required_tools list directly from Step 1. Only create tools if they are in the missing_tools list."""

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
    # model="meta-llama/Llama-3.1-8B-Instruct:novita",
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
    print("[Builder] Executing build pipeline...\n")

    asyncio.run(run_builder(user_instruction))
