"""
Gemini 2.0 Flash client — Priority 3, fast and good for lighter tasks.
Uses google-generativeai SDK.
"""
import os
import google.generativeai as genai


def call(system_prompt: str, user_prompt: str, max_tokens: int = 700) -> str:
    """Call Gemini 2.0 Flash and return the response text."""
    api_key ='AIzaSyCXHl-kx8Qop2GYhS7PqmSbEBOpGMxmChg'
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens,
        ),
    )
    print("model result:", model)

    response = model.generate_content(user_prompt)
    text = response.text or ""
    return text


system_prompt = "You are a helpful assistant that provides concise and accurate answers to user questions."

if __name__ == "__main__":
    user_prompt = "What is the capital of France?"
    response = call(system_prompt, user_prompt)
    print("Response:", response)