"""
Groq client — ultra-fast free inference via Groq Cloud.
No credit card needed. 14,400 requests/day free.
Model: llama-3.3-70b-versatile (best tool-calling quality on Groq)
Sign up: https://console.groq.com
"""
import os
from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700,
         task_type: str = "default") -> str:
    """Call Groq API and return the response text."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env")

    client = OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )

    return response.choices[0].message.content or ""
