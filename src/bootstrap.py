"""Pehli baar run par DB + docs auto-create (Render / Streamlit Cloud ke liye useful)."""
from src.config import DB_PATH, DOCS_DIR


def ensure_data():
    if not DB_PATH.exists():
        from scripts.build_db import build
        build()
    if not DOCS_DIR.exists() or not any(DOCS_DIR.glob("*.txt")):
        from scripts.build_docs import build
        build()
