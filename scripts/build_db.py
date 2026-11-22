"""Skills database banata hai (SQLite).   Run:  python -m scripts.build_db"""
import sqlite3
from src.config import DB_PATH
from src.seed_data import SKILLS, ROLES, COURSES, STUDENTS

SCHEMA = """
DROP TABLE IF EXISTS students;       DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS student_skills; DROP TABLE IF EXISTS job_roles;
DROP TABLE IF EXISTS role_skills;    DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS course_skills;

CREATE TABLE students(id INTEGER PRIMARY KEY, name TEXT, degree TEXT, year INTEGER);
CREATE TABLE skills(id INTEGER PRIMARY KEY, name TEXT UNIQUE, category TEXT);
CREATE TABLE student_skills(student_id INTEGER, skill_id INTEGER, level INTEGER);   -- level 1-5
CREATE TABLE job_roles(id INTEGER PRIMARY KEY, title TEXT UNIQUE, industry TEXT);
CREATE TABLE role_skills(role_id INTEGER, skill_id INTEGER, required_level INTEGER, importance REAL);
CREATE TABLE courses(id INTEGER PRIMARY KEY, name TEXT, provider TEXT, hours INTEGER);
CREATE TABLE course_skills(course_id INTEGER, skill_id INTEGER);
"""


def build(db_path=DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    skill_id = {}
    for name, cat in SKILLS.items():
        cur = con.execute("INSERT INTO skills(name, category) VALUES (?,?)", (name, cat))
        skill_id[name] = cur.lastrowid
    for title, info in ROLES.items():
        rid = con.execute("INSERT INTO job_roles(title, industry) VALUES (?,?)",
                          (title, info["industry"])).lastrowid
        for sk, (lvl, imp) in info["skills"].items():
            con.execute("INSERT INTO role_skills VALUES (?,?,?,?)", (rid, skill_id[sk], lvl, imp))
    for name, provider, hours, sks in COURSES:
        cid = con.execute("INSERT INTO courses(name, provider, hours) VALUES (?,?,?)",
                          (name, provider, hours)).lastrowid
        for sk in sks:
            con.execute("INSERT INTO course_skills VALUES (?,?)", (cid, skill_id[sk]))
    for name, degree, year, skills in STUDENTS:
        sid = con.execute("INSERT INTO students(name, degree, year) VALUES (?,?,?)",
                          (name, degree, year)).lastrowid
        for sk, lvl in skills.items():
            con.execute("INSERT INTO student_skills VALUES (?,?,?)", (sid, skill_id[sk], lvl))
    con.commit()
    con.close()
    return db_path


if __name__ == "__main__":
    print("DB created:", build())
