from tools_dir.registry import get_tool_list_string


def generate_system_prompt(user_instruction: str) -> dict:
    """
    Generate a full agent plan including system_prompt, goal, interval_hours, 
    and identified tools (required + missing).
    """
    tool_list = get_tool_list_string()
    system_msg = "You are an expert agent architect. Output only valid JSON. No markdown."

    user_msg = f"""User instruction: {user_instruction}

EXISTING TOOLS:
{tool_list}

PLANNING RULES:
1. Prefer existing tools. Only suggest "missing_tools" if no existing tool can perform the task.
2. For "system_prompt", write 60-80 words in the second person describing the agent's role.
3. For "goal", write a one-sentence instruction of exactly what to do.
4. For "interval_hours", detect repetition (daily=24, hourly=1, every 12h=12). Default is 0 (one-shot).

OUTPUT FORMAT:
{{
  "system_prompt": "...",
  "goal": "...",
  "interval_hours": 0,
  "required_tools": ["web_search", "send_email"],
  "missing_tools": [
    {{"name": "fetch_job_listings", "purpose": "search for AI engineer jobs on specific boards and return summaries"}}
  ]
}}"""

    for attempt in range(2):
        try:
            raw = call_llm("prompt_generation", user_msg, system_msg)

            # JSON extraction
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                raw = raw[start:end]

            result = json.loads(raw)

            # Ensure all keys exist
            defaults = {
                "system_prompt": f"You are an AI agent designed to: {user_instruction[:50]}",
                "goal": user_instruction,
                "interval_hours": 0,
                "required_tools": [],
                "missing_tools": []
            }
            for k, v in defaults.items():
                if k not in result:
                    result[k] = v
            
            return result

        except Exception:
            continue

    return {
        "system_prompt": f"You are an AI agent designed to: {user_instruction[:50]}",
        "goal": user_instruction,
        "interval_hours": 0,
        "required_tools": [],
        "missing_tools": []
    }
