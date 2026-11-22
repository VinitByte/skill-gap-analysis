# 🎯 Workforce Skill Gap Analysis & Career Recommendation System

Students learn skills in college, but employers ask for more practical and technical skills.
This project compares a student's skills with industry role requirements, shows the **skill gap**,
recommends **best-fit careers** and builds a **course roadmap**.

Extended from my earlier project *Agentic RAG Assistant with Safety Guardrails*
(multi-agent + RAG + SQLite + guardrails) - architecture reused, domain changed.

## Architecture
```
question + resume text
   |
[1 INPUT GUARD] + [2 PII REDACTION]
   |
 ROUTER -> gap analysis | career recommendation
   |
 PROFILE AGENT (skill extraction, validated vs taxonomy)
 RESEARCHER (RAG over job descriptions) [3 retrieval sanitiser]
 GAP ANALYST (SQL + weighted gap score) [4 tool budget] [5 SQL guard]
 RECOMMENDER (courses -> priority roadmap)
   |
 WRITER (no tools) -> [6 OUTPUT GUARD: canary, secrets, 'job guarantee' claims]
```
Gap score = sum(min(have, need) x importance) / sum(need x importance) x 100

## Run
```
pip install -r requirements.txt
python -m scripts.build_db && python -m scripts.build_docs
streamlit run streamlit_app.py
pytest -q
python -m eval.run_eval qa && python -m eval.run_eval attacks
```
LLM is optional: set `LLM_API_KEY` (e.g. free Groq key) in `.env` for resume parsing + nicer reports.
Without it the app runs in rule-based mode.

## What changed vs the old project
| Old (Agentic RAG) | New (Skill Gap) |
|---|---|
| 10 research PDFs | job-description documents (`data/docs`) |
| papers.db | skills.db: skills, roles, role_skills, courses, students |
| Researcher / Analyst agents | Profile, Researcher, Gap Analyst, Career, Recommender agents |
| SQL whitelist: papers tables | whitelist: skills/roles/courses; student tables private |
| - | PII redaction, hallucinated-skill filter, no-job-guarantee output check |
| QA accuracy eval | skill-extraction precision/recall, gap exact-match, attack block rate |
