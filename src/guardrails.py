"""Safety layers (pehle wale project ke guardrails + skill-gap domain ke naye checks).

1 check_input        - prompt injection / jailbreak / data-exfiltration intent
2 redact_pii         - NEW: resume se email / phone / Aadhaar hata deta hai
3 sanitize_retrieved - indirect injection (documents ke andar chhupi instructions)
4 ToolBudget         - loop / cost caps
5 validate_sql       - sirf SELECT, sirf whitelisted tables (students tables private)
6 check_output       - canary leak, secret redaction, NEW: 'job guarantee' claims
"""
import re
import unicodedata

from .config import CANARY, MAX_TOOL_CALLS

# ---------- 1. INPUT GUARD ----------
INJECTION_PATTERNS = [
    r"ignore (all |any )?(the )?(previous|prior|above|earlier) (instructions|prompts?|rules)",
    r"disregard (the |all )?(system|previous|above) (prompt|instructions)",
    r"(reveal|show|print|repeat|leak|display).{0,30}(system prompt|hidden instructions|your instructions|canary)",
    r"you are now (dan|an? unrestricted|an? evil)",
    r"developer mode", r"jailbreak",
    r"act as .{0,25}without (any )?(restrictions|rules|filters)",
    r"\bdrop\s+table\b", r"\btruncate\s+table\b", r"\bdelete\s+from\b",
    r"\bupdate\s+\w+\s+set\b", r"\binsert\s+into\b",
    r"(show|list|dump|give|display).{0,25}(all|every|other|another)\s+(student|user|record|profile)s?",
    r"(show|reveal|print|give|tell).{0,20}(api[_ ]?key|password|secret|token)",
]
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)


def _normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).translate(_ZERO_WIDTH).lower()
    return re.sub(r"\s+", " ", t)


def check_input(text: str):
    """returns (ok, reason)."""
    plain = _normalize(text)
    leet = plain.translate(_LEET)
    for pat in INJECTION_PATTERNS:
        if re.search(pat, plain) or re.search(pat, leet):
            return False, "Blocked by input guard: possible prompt-injection / unsafe request."
    return True, ""


# ---------- 2. PII REDACTION (new) ----------
_PII = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("AADHAAR", re.compile(r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")),
]


def redact_pii(text: str):
    """returns (clean_text, {'EMAIL': n, ...})."""
    counts = {}
    for label, rx in _PII:
        text, n = rx.subn(f"[{label} REDACTED]", text)
        if n:
            counts[label] = n
    return text, counts


# ---------- 3. RETRIEVAL SANITISER ----------
def sanitize_retrieved(text: str):
    """Documents ki un lines ko hata deta hai jo instructions jaisi dikhti hain. returns (clean, removed)."""
    kept, removed = [], 0
    for line in text.splitlines():
        plain = _normalize(line)
        if any(re.search(p, plain) or re.search(p, plain.translate(_LEET)) for p in INJECTION_PATTERNS) \
                or "guarantees a job" in plain:
            removed += 1
        else:
            kept.append(line)
    return "\n".join(kept), removed


# ---------- 4. LOOP / COST CAPS ----------
class ToolBudget:
    def __init__(self, max_calls=MAX_TOOL_CALLS):
        self.max_calls, self.calls, self.seen = max_calls, 0, set()

    def check(self, name, args=""):
        self.calls += 1
        key = (name, str(args))
        if self.calls > self.max_calls:
            raise RuntimeError("Tool-call budget exceeded")
        if key in self.seen:
            raise RuntimeError(f"Repeated identical tool call blocked: {name}")
        self.seen.add(key)


# ---------- 5. SQL GUARD ----------
# students / student_skills jaan-boojhkar list me NAHI hain: privacy (kisi aur student ka data nahi)
ALLOWED_TABLES = {"skills", "job_roles", "role_skills", "courses", "course_skills"}
_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|attach|pragma|replace|truncate|vacuum)\b", re.I)


def validate_sql(sql: str):
    """returns (ok, reason). Ek single SELECT, whitelisted tables only."""
    s = (sql or "").strip().rstrip(";").strip()
    if not s:
        return False, "Empty query"
    if ";" in s:
        return False, "Multiple statements not allowed"
    if "--" in s or "/*" in s:
        return False, "SQL comments not allowed"
    if not re.match(r"select\b", s, re.I):
        return False, "Only SELECT queries are allowed"
    if _FORBIDDEN.search(s):
        return False, "Forbidden SQL keyword"
    tables = re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", s, re.I)
    if not tables:
        return False, "No table referenced"
    bad = [t for t in tables if t.lower() not in ALLOWED_TABLES]
    if bad:
        return False, f"Table not allowed: {', '.join(bad)}"
    return True, ""


# ---------- 6. OUTPUT GUARD ----------
_SECRET = re.compile(r"(gsk_[A-Za-z0-9]{10,}|sk-[A-Za-z0-9]{10,})")
_GUARANTEE = re.compile(
    r"(guarantee[sd]?|100% (sure|certain)|will definitely get|surely get|assured (a )?job)", re.I)
DISCLAIMER = ("\n\n_Note: this report estimates skill alignment only. It cannot guarantee any job "
              "outcome - hiring depends on many other factors._")


def check_output(text: str):
    """returns (clean_text, flags)."""
    flags = []
    if CANARY in text:
        return "I can't share that. (Output blocked: internal configuration leak detected.)", ["canary_leak"]
    if _SECRET.search(text):
        text = _SECRET.sub("[REDACTED]", text)
        flags.append("secret_redacted")
    if _GUARANTEE.search(text):
        text = _GUARANTEE.sub("[claim removed]", text) + DISCLAIMER
        flags.append("guarantee_claim_removed")
    return text, flags
