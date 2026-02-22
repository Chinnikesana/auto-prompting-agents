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

    user_msg = f"""Write a Python function for this tool.

Tool name: {tool_name}
Purpose: {purpose}{error_note}

Requirements:
- Function name must be exactly: {tool_name}
- Single standalone function
- All imports at the top of the file (not inside the function)
- Always return a string
- Wrap main logic in try/except, return error message string on exception
- If the environment variable TOOL_TEST_MODE is set to "true", return a mock success string immediately without making real network calls or sending real emails
- Use only these packages if needed: requests, beautifulsoup4, smtplib, feedparser, duckduckgo-search
- No classes, no argparse, no if __name__ == "__main__" block

Output only the complete Python file content including imports."""

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
            "llm_used": "auto",
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
