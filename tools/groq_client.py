"""
Groq API client with round-robin key rotation.
At 4 keys × 14,400 req/day = 57,600 capacity vs ~20K needed.
"""
import random
import requests
from django.conf import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"


def _pick_key():
    keys = [k for k in settings.GROQ_API_KEYS if k and k.strip()]
    if not keys:
        raise RuntimeError(
            "No Groq API keys configured. Add GROQ_API_KEY_1 … GROQ_API_KEY_4 to .env"
        )
    return random.choice(keys)


def groq_chat(system_prompt: str, user_prompt: str, *, max_tokens: int = 1800, temperature: float = 0.7) -> str:
    """Call Groq and return the assistant reply text. Raises on HTTP error."""
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    resp = requests.post(
        GROQ_BASE_URL,
        headers={"Authorization": f"Bearer {_pick_key()}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
