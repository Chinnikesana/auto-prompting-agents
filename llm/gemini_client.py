"""
Gemini 2.0 Flash client — Priority 3, fast and good for lighter tasks.
Uses google-generativeai SDK.
"""
import os
import google.generativeai as genai
from core.config import Config


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700, model_name: str = "gemini-1.5-pro") -> str:
    """Call Gemini Pro and return the response text."""
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens,
        ),
    )

    response = model.generate_content(user_prompt)
    text = response.text or ""
    return text


system_prompt = "You are a helpful assistant that provides concise and accurate answers to user questions."

if __name__ == "__main__":
    user_prompt = "What is the capital of France?"
    response = call(system_prompt, user_prompt)
    print("Response:", response)