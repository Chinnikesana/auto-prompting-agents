"""
Hugging Face Router client — uses OpenAI-compatible API at https://router.huggingface.co/v1.
Provides access to models like Llama 3.1 8B via the Novita/other providers on HF.
"""
import os
import json
import requests as http_requests


# Models available on HF Router
MODELS = {
    "code_writing": "meta-llama/Llama-3.3-70B-Instruct",
    "prompt_generation": "meta-llama/Llama-3.3-70B-Instruct",
    "tool_identification": "meta-llama/Llama-3.3-70B-Instruct",
    "default": "meta-llama/Llama-3.3-70B-Instruct",
}

API_URL = "https://router.huggingface.co/v1/chat/completions"


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700,
         task_type: str = "default") -> str:
    """Call HF Router API and return the response text."""
    api_key = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY or HF_TOKEN not set")

    model = MODELS.get(task_type, MODELS["default"])

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
    }

    resp = http_requests.post(API_URL, headers=headers, json=payload, timeout=120)

    if resp.status_code == 429:
        raise RuntimeError("HF Router rate limit hit (429)")

    resp.raise_for_status()

    data = resp.json()

    if "choices" in data and len(data["choices"]) > 0:
        message = data["choices"][0].get("message", {})
        content = message.get("content", "")
        return content

    raise RuntimeError(f"Unexpected HF Router response: {json.dumps(data)[:300]}")
