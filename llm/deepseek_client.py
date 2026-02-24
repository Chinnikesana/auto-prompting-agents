"""
DeepSeek R1 client — Priority 1 for code writing tasks.
Uses OpenAI-compatible API at https://api.deepseek.com.
"""
import os
from openai import OpenAI


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700) -> str:
    """Call DeepSeek R1 and return the response text."""
    api_key = 'sk-86a6913c41c74f3ba31834aa9f3b5ec0'
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
    )

    text = response.choices[0].message.content or ""
    return text


if __name__ == "__main__":
    system_prompt = "You are a helpful assistant that provides concise and accurate answers to user questions."
    user_prompt = "What is the capital of France?"
    response = call(system_prompt, user_prompt)
    print("Response:", response)