"""
Hugging Face Inference API client — free hosted models.
Uses task-specific model selection:
  - Code writing: Meta Llama 4 Scout, Mixtral-8x7B
  - Text tasks: Mixtral-8x7B, Falcon-7B-Instruct
"""
import os
import time
import requests


# Model selection by task type — ordered by preference
MODELS = {
    "code_writing": [
        "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
    ],
    "prompt_generation": [
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "tiiuae/falcon-7b-instruct",
    ],
    "tool_identification": [
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "tiiuae/falcon-7b-instruct",
    ],
}

API_URL = "https://api-inference.huggingface.co/models"


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700,
         task_type: str = "code_writing") -> str:
    """Call HuggingFace Inference API and return the response text."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY not set")

    model_list = MODELS.get(task_type, MODELS["code_writing"])
    headers = {"Authorization": f"Bearer {api_key}"}

    # Try each model in the preference order
    last_error = None
    for model in model_list:
        url = f"{API_URL}/{model}"

        payload = {
            "inputs": f"<s>[INST] {system_prompt}\n\n{user_prompt} [/INST]",
            "parameters": {
                "max_new_tokens": max_tokens,
                "return_full_text": False,
            },
        }

        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=120)

                if resp.status_code == 503:
                    # Model is loading — wait and retry
                    body = resp.json()
                    wait_time = body.get("estimated_time", 30)
                    time.sleep(min(wait_time, 60))
                    continue

                if resp.status_code == 429:
                    raise RuntimeError("HuggingFace rate limit hit (429)")

                resp.raise_for_status()

                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    return data.get("generated_text", "")

                return str(data)

            except RuntimeError:
                raise
            except Exception as e:
                last_error = e
                break  # Try next model

    raise RuntimeError(
        f"HuggingFace API: all models failed. Last error: {last_error}"
    )
