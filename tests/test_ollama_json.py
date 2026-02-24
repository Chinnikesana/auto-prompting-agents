import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from llm import ollama_client

def test_ollama_json():
    print("Testing Ollama JSON mode and prompt suppression...")
    system_prompt = "You are a helpful assistant. Respond ONLY with valid JSON."
    user_prompt = "Generate a JSON with keys 'test' and 'success'."
    
    try:
        response = ollama_client.call(system_prompt, user_prompt)
        print(f"Response:\n{response}")
        
        import json
        data = json.loads(response)
        if "test" in data and "success" in data:
            print("✅ SUCCESS: Valid JSON returned.")
        else:
            print("❌ FAILURE: Missing keys in JSON.")
            
        if "<think>" in response or "</think>" in response:
            print("❌ FAILURE: Reasoning block found in response!")
        else:
            print("✅ SUCCESS: No reasoning blocks found.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_ollama_json()
