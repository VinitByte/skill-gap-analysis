"""Workforce Skill Gap Analysis & Career Recommendation System - web UI.
Run:  streamlit run streamlit_app.py"""
import pandas as pd
import streamlit as st

from src import llm, pipeline, tools
from src.bootstrap import ensure_data
from src.config import DOCS_DIR, POISONED_DIR

st.set_page_config(page_title="Skill Gap Analyzer", page_icon="🎯", layout="wide")
ensure_data()

st.title("🎯 Workforce Skill Gap Analysis & Career Recommendation")
st.caption("Compare your skills with industry requirements, find gaps and get a learning roadmap. "
           "Multi-agent RAG + SQL + safety guardrails.")

SAMPLE = ("B.Tech IT student. Skills: Python (3 years), basic SQL, HTML, CSS, Git, "
          "familiar with Excel and Pandas. Built a Flask REST API project.")

with st.sidebar:
    st.header("Settings")
    guard = st.toggle("Guardrails ON", value=True)
    poisoned = st.toggle("Use poisoned documents (attack demo)", value=False)
    st.write("LLM:", "✅ connected" if llm.available() else "⚪ off (rule-based mode)")
    st.divider()
    students = tools.list_students()
    demo = st.selectbox("Load demo student", ["-"] + [f"{s['id']} - {s['name']}" for s in students])

roles = tools.get_roles()
c1, c2 = st.columns([3, 2])
with c1:
    profile = st.text_area("Paste resume / skills text", value=SAMPLE, height=150)
    question = st.text_input("Your question (optional)", "What skills am I missing?")
with c2:
    target = st.selectbox("Target role", ["(suggest best roles for me)"] + roles)
    all_skills = tools.get_all_skills()
    manual = st.multiselect("Add skills manually (level 3)", all_skills)

manual_skills = {s: 3 for s in manual}
if demo != "-":
    manual_skills.update(tools.get_student_skills(int(demo.split(" - ")[0])))

if st.button("Analyze", type="primary"):
    res = pipeline.run(question, profile, manual_skills,
                       None if target.startswith("(") else target,
                       guardrails_on=guard, docs_dir=POISONED_DIR if poisoned else DOCS_DIR)
    if res["blocked"]:
        st.error(res["reason"])
        st.stop()
    if res["pii_redacted"]:
        st.warning(f"Personal data removed before analysis: {res['pii_redacted']}")
    if res["flags"]:
        st.info(f"Output guard flags: {res['flags']}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Skills detected", len(res["skills"]))
    if res["gap"]:
        m2.metric("Role match", f"{res['gap']['match_pct']}%")
        m3.metric("Gaps", len(res["gap"]["missing"]) + len(res["gap"]["weak"]))

    st.markdown(res["answer"])

    if res["gap"]:
        df = pd.DataFrame(res["gap"]["rows"])
        st.subheader("Your level vs required level")
        st.bar_chart(df.set_index("skill")[["have", "need"]])
        st.dataframe(df[["skill", "have", "need", "status", "priority"]], use_container_width=True)
    if res["roadmap"]:
        st.subheader("Learning roadmap")
        st.dataframe(pd.DataFrame(res["roadmap"]), use_container_width=True)
    with st.expander("Detected skills"):
        st.json(res["skills"])
    with st.expander("Retrieved industry sources (RAG)"):
        for s in res["sources"]:
            st.markdown(f"**{s['source']}** (score {s['score']})\n\n{s['text']}")
    with st.expander("Agent trace"):
        st.json(res["trace"])
