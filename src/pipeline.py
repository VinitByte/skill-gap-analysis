"""End-to-end pipeline: guard -> profile -> route -> analyse -> recommend -> write -> guard."""
from functools import lru_cache

from . import agents, guardrails
from .bootstrap import ensure_data
from .config import DOCS_DIR
from .retriever import Retriever


@lru_cache(maxsize=4)
def _retriever(docs_dir: str):
    return Retriever(docs_dir)


def run(question="", profile_text="", manual_skills=None, target_role=None,
        guardrails_on=True, docs_dir=None):
    ensure_data()
    result = {"blocked": False, "reason": "", "route": None, "skills": {}, "gap": None, "roles": [],
              "roadmap": [], "sources": [], "answer": "", "flags": [], "pii_redacted": {}, "trace": []}
    ctx = agents.AgentContext(guardrails_on)

    # [1] input guard + [2] PII redaction
    if guardrails_on:
        ok, reason = guardrails.check_input(f"{question}\n{profile_text}")
        if not ok:
            result.update(blocked=True, reason=reason, answer=f"Sorry - {reason}")
            return result
        profile_text, result["pii_redacted"] = guardrails.redact_pii(profile_text or "")
        question, _ = guardrails.redact_pii(question or "")

    skills = agents.profile_agent(ctx, profile_text, manual_skills)
    result["skills"] = skills

    role = target_role or agents.infer_role(question)
    result["route"] = agents.route(question, role)

    if result["route"] == "gap":
        retr = _retriever(str(docs_dir or DOCS_DIR))
        result["sources"] = agents.researcher_agent(ctx, retr, role)
        gap = agents.gap_agent(ctx, skills, role)
        result["gap"] = gap
        result["roadmap"] = agents.recommender_agent(ctx, gap)
    else:
        result["roles"] = agents.career_agent(ctx, skills)
        if result["roles"]:                      # best-fit role ka gap + roadmap bhi do
            top = result["roles"][0]["role"]
            result["gap"] = agents.gap_agent(ctx, skills, top)
            result["roadmap"] = agents.recommender_agent(ctx, result["gap"])

    answer = agents.writer_agent(ctx, question, skills, result["gap"] if result["route"] == "gap" else None,
                                 result["roles"], result["roadmap"], result["sources"])
    if guardrails_on:                                   # [6] output guard
        answer, result["flags"] = guardrails.check_output(answer)
    result["answer"], result["trace"] = answer, ctx.trace
    return result
