"""
Generate System Prompt — uses local Ollama (qwen3:8b) to plan the agent.
No API key needed. No rate limits. Fully offline.

The `generate_system_prompt()` function is called by the MCP server
(generate_system_prompt_server.py) and returns a dict with:
  system_prompt, goal, interval_hours, required_tools, missing_tools
"""
import os
import re
import json
import datetime
import requests

from tools_dir.registry import get_tool_list_string, get_registry
from db.collections import llm_logs

# ---------------------------------------------------------------------------
# Ollama local LLM call
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:8b"


def _strip_to_json(text: str) -> str:
    """
    Aggressively clean LLM output and extract the first valid JSON object.
    Handles: markdown fences, <think> blocks, leading prose, stray whitespace.
    """
    # 1. Kill any <think> ... </think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # 2. Strip markdown code fences
    text = re.sub(r"```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```", "", text)

    # 3. Extract outermost { ... }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    return text.strip()


def _call_ollama(system_prompt: str, user_prompt: str, max_tokens: int = 700) -> str:
    """
    Call local Ollama model.
    Returns a raw JSON string (no fences, no prose).
    Raises on failure.
    """
    model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)

    full_system = (
        f"{system_prompt}\n\n"
        "IMPORTANT: Output ONLY a valid JSON object. "
        "No markdown, no code fences, no explanation, no <think> blocks. "
        "Raw JSON only."
    )

    full_user = f"/no_think\n{user_prompt}"

    payload = {
        "model": model,
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": max_tokens,
        },
        "messages": [
            {"role": "system", "content": full_system},
            {"role": "user",   "content": full_user},
        ],
    }

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()

    raw = resp.json().get("message", {}).get("content", "") or ""
    print(f"[ollama] raw response:\n{raw}\n")

    cleaned = _strip_to_json(raw)

    # Validate it's actually JSON before returning
    try:
        json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"[ollama] Response is not valid JSON after cleaning.\n"
            f"Error: {e}\n"
            f"Cleaned text: {cleaned[:300]}"
        )

    return cleaned


# ---------------------------------------------------------------------------
# Main function — called by the MCP server
# ---------------------------------------------------------------------------
def generate_system_prompt(user_instruction: str) -> dict:
    """
    Generate a full agent plan including system_prompt, goal, interval_hours,
    and identified tools (required + missing).

    Uses local Ollama (qwen3:8b) — no API key, no rate limits.

    Returns dict on success, raises RuntimeError on failure.
    """
    tool_list = get_tool_list_string()
    print(f"[generate_system_prompt] available tools:\n{tool_list}\n")

    system_msg = (
        "You are an expert agent architect. "
        "Output ONLY a valid JSON object. No markdown, no explanation, no code fences.\n"
        "/no_think"
    )

    user_msg = f"""USER INSTRUCTION:
{user_instruction}

---
AVAILABLE TOOLS (select ONLY from this list):
{tool_list}

---
RULES:
1. required_tools -- pick tool names from the AVAILABLE TOOLS list above that are needed for this task. MUST be a JSON array of exact tool name strings.
2. missing_tools -- ONLY if a needed capability is completely absent from the list above. MUST be a JSON array of objects. Each object MUST have:
   - "name": a short snake_case tool name (e.g. "job_scraper")
   - "purpose": a DETAILED paragraph (3-5 sentences) explaining exactly what this tool should do, what inputs it takes, what output it returns, and any libraries it should use. This purpose will be given directly to a code-generation LLM to write the tool, so be very specific.
3. system_prompt -- 2-3 sentences describing the agent role in second person (e.g. "You are an AI agent that ...").
4. goal -- one sentence, the exact task the agent should execute.
5. interval_hours -- 0 for one-shot, 24 for daily, 1 for hourly.

Respond with ONLY this JSON, nothing else:
{{
  "system_prompt": "You are an AI agent that ...",
  "goal": "...",
  "interval_hours": 0,
  "required_tools": ["web_search", "send_email"],
  "missing_tools": [{{"name": "example_tool", "purpose": "Detailed paragraph about what this tool does..."}}]
}}"""

    # Get valid tool names for validation
    valid_tool_names = {t["name"] for t in get_registry() if t["status"] == "active"}

    last_error = None
    for attempt in range(2):
        try:
            raw = _call_ollama(system_msg, user_msg)

            print(f"[generate_system_prompt] raw LLM response (attempt {attempt+1}):\n{raw}\n")

            # JSON extraction
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0 or end <= start:
                raise ValueError(f"No JSON object found in response: {raw[:200]}")
            json_str = raw[start:end]
            print(f"[generate_system_prompt] extracted JSON:\n{json_str}\n")

            result = json.loads(json_str)

            # Ensure all keys exist with correct types
            required_keys = ["system_prompt", "goal", "interval_hours", "required_tools", "missing_tools"]
            for k in required_keys:
                if k not in result:
                    raise ValueError(f"LLM response missing required key: '{k}'. Got keys: {list(result.keys())}")

            # Ensure lists are actually lists
            if not isinstance(result["required_tools"], list):
                raise ValueError(f"required_tools must be a list, got: {type(result['required_tools'])}")
            if not isinstance(result["missing_tools"], list):
                raise ValueError(f"missing_tools must be a list, got: {type(result['missing_tools'])}")

            # Validate required_tools -- remove any names not in registry
            invalid = [t for t in result["required_tools"] if t not in valid_tool_names]
            if invalid:
                print(f"[generate_system_prompt] WARNING: removing invalid tool names (not in registry): {invalid}")
                result["required_tools"] = [t for t in result["required_tools"] if t in valid_tool_names]

            # Validate missing_tools format
            for i, mt in enumerate(result["missing_tools"]):
                if not isinstance(mt, dict) or "name" not in mt or "purpose" not in mt:
                    raise ValueError(f"missing_tools[{i}] must be a dict with 'name' and 'purpose', got: {mt}")

            print(f"[generate_system_prompt] plan ready:")
            print(f"  system_prompt : {result['system_prompt'][:80]}...")
            print(f"  goal          : {result['goal']}")
            print(f"  interval_hours: {result['interval_hours']}")
            print(f"  required_tools: {result['required_tools']}")
            print(f"  missing_tools : {result['missing_tools']}")

            # Store plan in MongoDB for traceability
            try:
                llm_logs().insert_one({
                    "task_type": "agent_plan",
                    "user_instruction": user_instruction,
                    "tools_sent_to_llm": tool_list,
                    "plan": result,
                    "timestamp": datetime.datetime.utcnow(),
                })
            except Exception:
                pass

            return result

        except Exception as e:
            last_error = e
            print(f"[generate_system_prompt] attempt {attempt+1} failed: {e}")
            continue

    # No fallback -- raise error so the builder agent knows it failed
    raise RuntimeError(
        f"[generate_system_prompt] All attempts failed. Last error: {last_error}"
    )