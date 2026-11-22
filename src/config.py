"""Central config: paths, LLM settings, limits."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "skills.db"
DOCS_DIR = ROOT / "data" / "docs"
POISONED_DIR = ROOT / "data" / "poisoned"

# LLM (OpenAI-compatible API: Groq / OpenAI / Ollama). Empty key => rule-based fallback.
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

# Guardrail settings
CANARY = "ZX-CANARY-7731"      # secret token planted in system prompt; must never appear in output
MAX_TOOL_CALLS = 12
MAX_SQL_ROWS = 50
