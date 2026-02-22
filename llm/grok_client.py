"""
Grok 2 client — Priority 2 fallback.
Uses OpenAI-compatible API at https://api.x.ai/v1.
"""
import os
from openai import OpenAI


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700) -> str:
    """Call Grok 2 and return the response text."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
    )

    text = response.choices[0].message.content or ""
    return text
