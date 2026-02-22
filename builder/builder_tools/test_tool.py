"""
test_tool — Builder tool that runs a newly created tool in a sandbox subprocess.
"""
from tests.sandbox_runner import run_tool_test


def test_tool(tool_name: str, file_path: str) -> dict:
    """
    Test a tool by running it in an isolated subprocess.

    Returns:
        dict with keys: passed (bool), output (str), error (str)
    """
    return run_tool_test(tool_name, file_path)
