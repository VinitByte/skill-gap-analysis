"""Agent tools. Sab database-backed hain; gap math deterministic hai (LLM se nahi karwaya)."""
import re
import sqlite3

from .config import DB_PATH, MAX_SQL_ROWS
from .guardrails import validate_sql
from .seed_data import ALIASES


def _conn(readonly=True):
    if readonly:                                   # defence in depth: DB read-only open
        return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    return sqlite3.connect(DB_PATH)


def _rows(sql, params=()):
    con = _conn()
    try:
        cur = con.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        con.close()


# ---------- generic SQL tool (guarded) ----------
def sql_query(sql: str):
    ok, reason = validate_sql(sql)
    if not ok:
        raise ValueError(f"SQL blocked: {reason}")
    return _rows(sql)[:MAX_SQL_ROWS]


# ---------- lookups ----------
def get_all_skills():
    return [r["name"] for r in _rows("SELECT name FROM skills ORDER BY name")]


def get_roles():
    return [r["title"] for r in _rows("SELECT title FROM job_roles ORDER BY title")]


def get_role_requirements(role: str):
    return _rows("""SELECT s.name AS skill, rs.required_level, rs.importance
                    FROM role_skills rs JOIN job_roles r ON r.id = rs.role_id
                    JOIN skills s ON s.id = rs.skill_id
                    WHERE lower(r.title) = lower(?) ORDER BY rs.importance DESC, s.name""", (role,))


def get_student_skills(student_id: int):
    """Demo students ke liye (sirf us student ki apni skills)."""
    rows = _rows("""SELECT s.name AS skill, ss.level FROM student_skills ss
                    JOIN skills s ON s.id = ss.skill_id WHERE ss.student_id = ?""", (student_id,))
    return {r["skill"]: r["level"] for r in rows}


def list_students():
    return _rows("SELECT id, name, degree, year FROM students ORDER BY id")


# ---------- skill extraction (resume text -> {skill: level}) ----------
_STRONG = re.compile(r"advanced|expert|proficient|strong|experienced|\b[3-9]\+?\s*years?", re.I)
_WEAK = re.compile(r"basic|beginner|familiar|learning|exposure|introductory", re.I)


def filter_known_skills(skills: dict):
    """Hallucination guard: sirf taxonomy me maujood skills rakho, level 1-5 me clamp karo."""
    known = {s.lower(): s for s in get_all_skills()}
    out = {}
    for name, lvl in skills.items():
        canon = known.get(str(name).strip().lower())
        if canon:
            try:
                out[canon] = max(1, min(5, int(lvl)))
            except (TypeError, ValueError):
                out[canon] = 3
    return out


def extract_skills(text: str):
    """Rule-based extractor: taxonomy names + aliases, level keywords se guess."""
    known = {s.lower(): s for s in get_all_skills()}
    terms = {**known, **{a.lower(): c for a, c in ALIASES.items()}}
    found = {}
    for term, canon in sorted(terms.items(), key=lambda kv: -len(kv[0])):
        for m in re.finditer(r"(?<![\w])" + re.escape(term) + r"(?![\w])", text, re.I):
            # level sirf usi skill ke segment se guess karo (comma / newline / ; / | tak)
            start = max(text.rfind(ch, 0, m.start()) for ch in ",;\n|") + 1
            ends = [i for i in (text.find(ch, m.end()) for ch in ",;\n|") if i != -1]
            window = text[start: min(ends) if ends else len(text)]
            lvl = 4 if _STRONG.search(window) else 2 if _WEAK.search(window) else 3
            found[canon] = max(found.get(canon, 0), lvl)
    return found


# ---------- CORE: skill gap ----------
def compute_skill_gap(student_skills: dict, role: str):
    """Weighted match: sum(min(have, need) * importance) / sum(need * importance)."""
    reqs = get_role_requirements(role)
    if not reqs:
        raise ValueError(f"Unknown role: {role}")
    have_map = {k.lower(): int(v) for k, v in student_skills.items()}
    rows, score, total = [], 0.0, 0.0
    for r in reqs:
        have, need, imp = have_map.get(r["skill"].lower(), 0), r["required_level"], r["importance"]
        score += min(have, need) * imp
        total += need * imp
        status = "matched" if have >= need else "weak" if have > 0 else "missing"
        rows.append({"skill": r["skill"], "have": have, "need": need, "importance": imp,
                     "status": status, "priority": round((need - have) * imp, 2) if have < need else 0.0})
    return {"role": role, "match_pct": round(100 * score / total, 1), "rows": rows,
            "matched": [r["skill"] for r in rows if r["status"] == "matched"],
            "weak": [r["skill"] for r in rows if r["status"] == "weak"],
            "missing": [r["skill"] for r in rows if r["status"] == "missing"]}


def suggest_roles(student_skills: dict, top_n=3):
    """Sabhi roles ke against match% nikaal ke best-fit careers do."""
    scored = []
    for role in get_roles():
        g = compute_skill_gap(student_skills, role)
        scored.append({"role": role, "match_pct": g["match_pct"], "missing": g["missing"], "weak": g["weak"]})
    return sorted(scored, key=lambda x: -x["match_pct"])[:top_n]


def recommend_courses(gap: dict):
    """Gap skills ko priority ke order me course roadmap me badlo (kam hours wala course pehle)."""
    todo = sorted([r for r in gap["rows"] if r["status"] != "matched"], key=lambda r: -r["priority"])
    roadmap = []
    for r in todo:
        courses = _rows("""SELECT c.name, c.provider, c.hours FROM courses c
                           JOIN course_skills cs ON cs.course_id = c.id
                           JOIN skills s ON s.id = cs.skill_id
                           WHERE s.name = ? ORDER BY c.hours LIMIT 1""", (r["skill"],))
        c = courses[0] if courses else None
        roadmap.append({"skill": r["skill"], "status": r["status"], "priority": r["priority"],
                        "course": c["name"] if c else None,
                        "provider": c["provider"] if c else None,
                        "hours": c["hours"] if c else None})
    return roadmap
