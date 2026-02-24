"""
Ollama local client — uses Ollama's native /api/chat endpoint at localhost:11434.
No API key needed. No rate limits. Fully offline.
Recommended model: qwen3:8b  (pull with: ollama pull qwen3:8b)

Thinking mode is DISABLED via:
  1. "think": false  — Ollama native parameter
  2. /no_think token — qwen3 native instruction
  3. System prompt instruction — explicit suppression
"""
import os
import re
import requests
import json

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:8b"


# def call(system_prompt: str, user_prompt: str, max_tokens: int = 700,
#          task_type: str = "default") -> str:
#     """Call local Ollama model with thinking mode disabled and JSON format enabled."""
#     model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)

#     # Force suppress reasoning via system prompt + /no_think token
#     system_prompt += "\nIMPORTANT: Do not include any reasoning, internal thoughts, or <think> blocks. Output ONLY the raw response.\n/no_think"

#     # Use Ollama's native /api/chat endpoint
#     payload = {
#         "model": model,
#         "stream": False,
#         "think": False,           # Ollama native: disables <think> blocks
#         "format": "json",         # forces JSON output, skips prose
#         "options": {
#             "temperature": 0.1,   # lower = more deterministic
#             "num_predict": max_tokens,
#         },
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user",   "content": user_prompt},
#         ],
#     }

#     resp = requests.post(
#         f"{OLLAMA_BASE_URL}/api/chat",
#         json=payload,
#         timeout=120,
#     )
#     resp.raise_for_status()

#     data = resp.json()
#     text = data.get("message", {}).get("content", "") or ""

#     # Safety strip — remove any stray <think> blocks just in case
#     text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
#     # Remove markdown code fences if model wraps JSON
#     text = re.sub(r"^```[a-zA-Z]*\n?", "", text, flags=re.MULTILINE)
#     text = re.sub(r"\n?```$", "", text, flags=re.MULTILINE)
#     return text.strip()


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700,
         task_type: str = "default") -> str:
    model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)

    system_prompt += "\nIMPORTANT: Do not include any reasoning or <think> blocks. Output ONLY the raw response."

    payload = {
        "model": model,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.1,
            "num_predict": max_tokens,
        },
        "messages": [
            {"role": "system", "content": system_prompt},
            # /no_think goes at the START of the user message
            {"role": "user", "content": f"/no_think {user_prompt}"},
        ],
    }

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()

    data = resp.json()
    text = data.get("message", {}).get("content", "") or ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return text.strip()

if __name__ == "__main__":
    system_prompt = "You are a helpful assistant that provides concise and accurate answers to user questions."
    user_prompt = ""
    response = call(system_prompt, user_prompt)
    print("Response:", response)