"""
create_new_tool — Builder tool that asks the LLM to write a new tool function
and saves it as a file in tools_dir/.
"""
import os
import re
import datetime
from llm.llm_router import call_llm
from db.collections import tool_creation_logs


def create_new_tool(tool_name: str, purpose: str, agent_id: str = "",
                    attempt: int = 1, previous_error: str = "") -> str:
    """
    Generate a new tool using the LLM and write it to tools_dir/{tool_name}.py.

    Returns:
        File path of the written tool.

    Raises:
        RuntimeError if the generated code is invalid.
    """
    system_msg = (
        "You are a Python expert. Write clean, working Python code. "
        "Output only Python code. No explanation. No markdown fences."
    )

    error_note = ""
    if attempt > 1 and previous_error:
        error_note = f'\nPrevious attempt failed with this error: {previous_error}. Fix this issue.'

    user_msg = f"""You are building a tool for an AI agent. 
Use the context and requirements below to write a high-quality, standalone Python function.

TOOL NAME: {tool_name}
CONTEXT & PURPOSE:
{purpose}
{error_note}

TECHNICAL REQUIREMENTS:
- Function name MUST be exactly: {tool_name}
- This must be a single standalone function in a plain Python file.
- All imports (requests, bs4, etc.) MUST be at the top of the file.
- The function MUST always return a string (either the result or an error message).
- Wrap the main logic in a try/except block.
- MOCK MODE: If the environment variable TOOL_TEST_MODE is "true", return a mock success string immediately. Do NOT make real network calls or send real emails in mock mode.
- LIBS: Use only these packages if needed: requests, beautifulsoup4, smtplib, feedparser, duckduckgo-search.
- Constraints: No classes, no argparse, no if __name__ == "__main__" block.

Output ONLY the complete Python file content. No conversation, no markdown fences."""

    raw_code = call_llm("code_writing", user_msg, system_msg)

    # Strip any accidental markdown fences
    code = re.sub(r"^```[a-zA-Z]*\n?", "", raw_code, flags=re.MULTILINE)
    code = re.sub(r"\n?```$", "", code, flags=re.MULTILINE)
    code = code.strip()

    # Validate the code contains the expected function definition
    if f"def {tool_name}" not in code:
        raise RuntimeError(
            f"Generated code does not contain 'def {tool_name}'. "
            f"Got: {code[:200]}"
        )

    # Write to file
    file_path = os.path.join("tools_dir", f"{tool_name}.py")
    os.makedirs("tools_dir", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Log to MongoDB
    try:
        tool_creation_logs().insert_one({
            "tool_name": tool_name,
            "requested_for_agent": agent_id,
            "attempt_number": attempt,
            "llm_used": "gemini",
            "purpose_sent": purpose,
            "code_written": code,
            "test_passed": None,
            "test_output": None,
            "error_message": None,
            "created_at": datetime.datetime.utcnow(),
        })
    except Exception:
        pass

    return file_path
