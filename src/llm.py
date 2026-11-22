"""Optional LLM client (OpenAI-compatible: Groq / OpenAI / Ollama). Key na ho to available() False."""
import requests

from . import config


def available() -> bool:
    return bool(config.LLM_API_KEY)


def chat(messages, temperature=0.2, timeout=40) -> str:
    r = requests.post(
        f"{config.LLM_BASE_URL.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
        json={"model": config.LLM_MODEL, "messages": messages, "temperature": temperature},
        timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
