"""
LLM Router — unified interface for all LLM interactions.
Handles provider fallback, rate-limit tracking, response cleanup, and logging.

All models used are FREE:
  - DeepSeek R1 (free tier) — strongest reasoning for code
  - Gemini 2.0 Flash (free tier) — fast, good for prompts/planning
  - OpenRouter (free models) — arcee-ai/trinity for general reasoning
  - HuggingFace (free inference) — Llama 4, Mixtral, Falcon

Usage:
    from llm.llm_router import call_llm
    result = call_llm("code_writing", "Write a function...", "You are a Python expert.")
"""
import os
import re
import time
import datetime
from llm import deepseek_client, gemini_client, huggingface_client, hf_router_client, ollama_client, groq_client
from db.collections import llm_logs

# ---------------------------------------------------------------------------
# Provider priority by task type
# groq = Groq Cloud (llama-3.3-70b, ~250 tok/sec, free tier)
# ollama = local qwen3:8b (fallback, no API key, fully offline)
# ---------------------------------------------------------------------------
PRIORITY = {
    "code_writing":       ["groq", "ollama", "deepseek", "gemini", "hf_router", "huggingface"],
    "prompt_generation":  ["groq", "ollama", "gemini",  "deepseek", "hf_router", "huggingface"],
    "tool_identification":["groq", "ollama", "gemini",  "deepseek", "hf_router", "huggingface"],
}

# Max tokens by task type
MAX_TOKENS = {
    "code_writing": 700,
    "prompt_generation": 600,   # needs enough room for full JSON with system_prompt + tools
    "tool_identification": 400,
}

# In-memory rate-limit tracker: provider -> timestamp of last 429
_rate_limited: dict[str, float] = {}
RATE_LIMIT_COOLDOWN = 60  # seconds


# ---------------------------------------------------------------------------
# Response cleanup helpers
# ---------------------------------------------------------------------------
def _strip_think_blocks(text: str) -> str:
    """Remove DeepSeek <think>...</think> reasoning blocks."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences (```python ... ```)."""
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n?```$", "", text, flags=re.MULTILINE)
    return text.strip()


# ---------------------------------------------------------------------------
# Provider dispatch
# ---------------------------------------------------------------------------
def _call_provider(provider: str, system_prompt: str, user_prompt: str,
                   max_tokens: int, task_type: str) -> str:
    """Call a single LLM provider. Raises on failure."""
    if provider == "groq":
        return groq_client.call(system_prompt, user_prompt, max_tokens)
    elif provider == "ollama":
        return ollama_client.call(system_prompt, user_prompt, max_tokens, task_type)
    elif provider == "deepseek":
        return deepseek_client.call(system_prompt, user_prompt, max_tokens)
    elif provider == "gemini":
        return gemini_client.call(system_prompt, user_prompt, max_tokens)
    elif provider == "hf_router":
        return hf_router_client.call(system_prompt, user_prompt, max_tokens, task_type)
    elif provider == "huggingface":
        return huggingface_client.call(system_prompt, user_prompt, max_tokens, task_type)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _is_rate_limited(provider: str) -> bool:
    """Check if provider was rate-limited within the cooldown window."""
    ts = _rate_limited.get(provider)
    if ts is None:
        return False
    if time.time() - ts > RATE_LIMIT_COOLDOWN:
        del _rate_limited[provider]
        return False
    return True


def _mark_rate_limited(provider: str):
    """Mark a provider as rate-limited right now."""
    _rate_limited[provider] = time.time()


def _is_rate_limit_error(exc: Exception) -> bool:
    """Check if an exception indicates a 429 rate limit."""
    msg = str(exc).lower()
    return "429" in msg or "rate" in msg


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def _get_priority(task_type: str) -> list:
    """Return provider priority, putting PREFERRED_LLM first if set."""
    base = list(PRIORITY.get(task_type, PRIORITY["code_writing"]))
    preferred = os.getenv("PREFERRED_LLM", "").lower()
    if preferred and preferred in base:
        base.remove(preferred)
        base.insert(0, preferred)
    return base


def call_llm(task_type: str, prompt: str, system_prompt: str = "") -> str:
    """
    Call the best available free LLM for the given task type.

    Args:
        task_type: One of "code_writing", "prompt_generation", "tool_identification".
        prompt: The user/instruction prompt.
        system_prompt: The system message for the LLM.

    Returns:
        Cleaned response string.
    """
    providers = _get_priority(task_type)
    max_tokens = MAX_TOKENS.get(task_type, 700)

    last_error = None
    for provider in providers:
        if _is_rate_limited(provider):
            continue

        start = time.time()
        fallback_used = provider != providers[0]
        try:
            raw = _call_provider(provider, system_prompt, prompt, max_tokens, task_type)
            duration_ms = int((time.time() - start) * 1000)

            # Cleanup
            text = _strip_think_blocks(raw)
            text = _strip_code_fences(text)

            # Log success
            _log(task_type, provider, prompt, text, True, fallback_used, None, duration_ms)
            return text

        except Exception as exc:
            duration_ms = int((time.time() - start) * 1000)
            last_error = exc

            if _is_rate_limit_error(exc):
                _mark_rate_limited(provider)
                reason = "rate_limit"
            else:
                reason = str(exc)[:200]

            _log(task_type, provider, prompt, "", False, fallback_used, reason, duration_ms)
            continue

    raise RuntimeError(
        f"All LLM providers failed for task_type={task_type}. Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# MongoDB logging
# ---------------------------------------------------------------------------
def _log(task_type: str, provider: str, prompt: str, response: str,
         success: bool, fallback_used: bool, fallback_reason: str | None,
         duration_ms: int):
    """Log an LLM call to MongoDB with full prompt and response text."""
    try:
        models = {
            "groq": "groq/llama-3.3-70b-versatile",
            "ollama": f"ollama/{os.getenv('OLLAMA_MODEL', 'qwen3:8b')}",
            "deepseek": "deepseek-reasoner",
            "gemini": "gemini-2.0-flash-exp",
            "hf_router": "meta-llama/Llama-3.3-70B-Instruct",
            "huggingface": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        }
        llm_logs().insert_one({
            "task_type": task_type,
            "model_used": models.get(provider, provider),
            "provider": provider,
            # full text stored
            "prompt_text": prompt,
            "response_text": response,
            # char counts for quick stats
            "prompt_length_chars": len(prompt),
            "response_length_chars": len(response),
            "success": success,
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
            "duration_ms": duration_ms,
            "timestamp": datetime.datetime.utcnow(),
        })
    except Exception:
        pass  # Never let logging break the main flow
