"""
Sandbox runner — runs a tool function in an isolated subprocess for testing.
"""
import os
import sys
import subprocess
import tempfile


def run_tool_test(tool_name: str, tool_file_path: str) -> dict:
    """
    Run a tool in an isolated subprocess to check it imports and executes.

    Returns:
        dict with keys: passed (bool), output (str), error (str)
    """
    # Create temp test directory
    temp_dir = os.path.join("tests", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    test_file = os.path.join(temp_dir, f"{tool_name}_test.py")

    # Write the test script
    test_code = f'''import sys
sys.path.insert(0, ".")
from tools_dir.{tool_name} import {tool_name}

try:
    result = {tool_name}("test")
    if isinstance(result, str):
        print("PASS:" + result[:100])
    else:
        print("PASS:returned non-string but no exception")
except TypeError:
    try:
        result = {tool_name}()
        print("PASS:" + str(result)[:100])
    except Exception as e:
        print("FAIL:" + str(e))
except Exception as e:
    print("FAIL:" + str(e))
'''

    try:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code)

        # Set up environment with TOOL_TEST_MODE=true
        env = os.environ.copy()
        env["TOOL_TEST_MODE"] = "true"

        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
            cwd=".",
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stdout.startswith("PASS:"):
            return {
                "passed": True,
                "output": stdout[5:],
                "error": "",
            }
        elif stdout.startswith("FAIL:"):
            return {
                "passed": False,
                "output": "",
                "error": stdout[5:],
            }
        else:
            # Check if there was a traceback in stderr
            if stderr:
                return {
                    "passed": False,
                    "output": stdout,
                    "error": stderr[:500],
                }
            return {
                "passed": False,
                "output": stdout,
                "error": "Unexpected output format",
            }

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "output": "",
            "error": "Tool execution timed out after 15 seconds",
        }
    except Exception as e:
        return {
            "passed": False,
            "output": "",
            "error": str(e),
        }
    finally:
        # Cleanup temp test file
        try:
            os.remove(test_file)
        except Exception:
            pass
