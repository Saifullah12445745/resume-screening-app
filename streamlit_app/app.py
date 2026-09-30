"""Standalone Streamlit interface using the shared screening engine."""
import hashlib
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from screening import SKILLS, export_csv, extract_skills, extract_text, skill_comparison

st.set_page_config(page_title="Resume Studio | Screening workspace", page_icon="✦", layout="wide")
st.markdown("""
<style>
.stApp {background: radial-gradient(ellipse at 85% 0%, #29204b 0%, transparent 42%), #0b1020;}
.block-container {max-width:1200px;padding-top:2.2rem;padding-bottom:3rem;}
[data-testid="stSidebar"] {background:#11172a;border-right:1px solid #293047;}
[data-testid="stMetric"] {background:#151c31;border:1px solid #303951;border-radius:16px;padding:18px;}
.hero {padding:30px;border:1px solid #49406b;border-radius:22px;background:linear-gradient(120deg,#252044,#142638);margin-bottom:24px;}
.eyebrow {color:#bcb0ff;font-size:12px;letter-spacing:3px;font-weight:700;}
.hero h1 {font-size:clamp(2rem,5vw,3.3rem);letter-spacing:-1.5px;margin:8px 0;}
.hero p {color:#c5cee1;max-width:640px;margin-bottom:0;}
.stButton button[kind="primary"] {background:#8061ec;border:0;}
</style>
<div class="hero"><div class="eyebrow">RESUME STUDIO / REVIEW WORKSPACE</div>
<h1>Find the skills.<br>See the evidence.</h1>
<p>A focused workspace to compare resumes, explore skill coverage and build your shortlist.</p></div>
""", unsafe_allow_html=True)

DEMO_JOB = "Python backend developer with SQL, FastAPI, Docker and Git experience."
DEMO_FILES = [
    ("Alex - sample.txt", b"SYNTHETIC DEMO RESUME\nAlex | Backend developer\nBuilt Python and FastAPI services with SQL databases. Used Docker and Git for delivery."),
    ("Sam - sample.txt", b"SYNTHETIC DEMO RESUME\nSam | Data analyst\nUses Python, SQL, pandas and Excel. Tracks projects with Git."),
    ("Jordan - sample.txt", b"SYNTHETIC DEMO RESUME\nJordan | Frontend developer\nBuilds React interfaces with JavaScript, HTML and CSS. Uses Git."),
]

def clear_results():
    for key in list(st.session_state):
        if key.startswith("pick_") or key in ("results", "snapshot", "issues"):
            del st.session_state[key]

def reset_workspace():
    st.session_state.clear()

def load_demo():
    clear_results()
    st.session_state["demo"] = True
    st.session_state["job"] = DEMO_JOB
    st.session_state["skills"] = ["python", "sql", "fastapi", "docker", "git"]
    st.session_state["custom"] = ""

def detect_skills():
    st.session_state["skills"] = extract_skills(st.session_state.get("job", ""))

with st.sidebar:
    st.markdown("### ✦ Resume Studio")
    st.caption("A clearer view of every application")
    st.divider()
    st.markdown("**Your workflow**")
    st.markdown("1. Define the role\n2. Add resumes\n3. Review & shortlist")
    st.divider()
    st.button("Try sample workspace", on_click=load_demo, use_container_width=True)
    st.button("Clear workspace", on_click=reset_workspace, use_container_width=True)
    st.caption("Skills-only matching • No API key needed")
    st.caption("Files are processed on the server. This app does not intentionally save resumes to disk or a database. Results and shortlist stay in your current session.")
    st.caption("Use sample files for public demos.")

left, right = st.columns([1.15, 1], gap="large")
with left:
    st.subheader("01 / Define the role")
    job = st.text_area("Job description", key="job", height=180, max_chars=20000,
                       placeholder="Paste responsibilities and skills for the role…")
    st.button("Detect skills from description", on_click=detect_skills)
    selected = st.multiselect("Required skills", SKILLS, key="skills")
    custom = st.text_input("Additional skills, separated by commas", key="custom",
                           max_chars=2000, placeholder="e.g. Redis, Terraform")
    required = sorted(set(selected + [s.strip().lower() for s in custom.split(",") if s.strip()]))
    st.caption("Ranking uses the required skills above. Review detected skills before screening.")

with right:
    st.subheader("02 / Add resumes")
    uploads = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"],
                               accept_multiple_files=True, key="uploads")
    st.caption("Up to 20 resumes • 10 MB per file • 25 MB total. Scanned PDFs require OCR.")
    demo = st.checkbox("Use synthetic sample resumes", key="demo")
    if demo and not uploads:
        st.info("Three sample resumes are ready. Click Screen resumes below.")
    elif demo and uploads:
        st.caption("Your uploads take precedence over sample resumes.")
    st.markdown("**Transparent scoring**")
    st.caption("Coverage = matched required skills ÷ all required skills. A score is not a hiring recommendation or proof of proficiency.")

files = [(f.name, f.getvalue()) for f in uploads] if uploads else (DEMO_FILES if demo else [])
signature = (job, tuple(required), tuple((name, hashlib.sha256(data).hexdigest()) for name, data in files))

if st.button("Screen resumes →", type="primary", use_container_width=True):
    clear_results()
    if not required:
        st.error("Select or detect at least one required skill.")
    elif len(required) > 100 or any(len(s) > 100 for s in required):
        st.error("Use at most 100 required skills, each no longer than 100 characters.")
    elif not files:
        st.error("Upload resumes or enable the sample workspace.")
    elif len(files) > 20 or sum(len(data) for _, data in files) > 25 * 1024 * 1024:
        st.error("Use at most 20 files and keep the combined upload below 25 MB.")
    else:
        results, issues, seen = [], [], set()
        with st.spinner("Reading resumes and checking skills…"):
            for index, (name, data) in enumerate(files):
                digest = hashlib.sha256(data).hexdigest()
                if digest in seen:
                    issues.append(f"{name}: identical content already included; skipped.")
                    continue
                seen.add(digest)
                try:
                    text = extract_text(name, data)
                    matched, missing, coverage = skill_comparison(text, required)
                    results.append({"id": digest, "name": name, "text": text,
                                    "matched": matched, "missing": missing, "coverage": coverage})
                except Exception:
                    issues.append(f"{name}: could not read this file. Check that it is a valid, nonempty PDF, DOCX or UTF-8 TXT below 10 MB. Scanned PDFs need OCR.")
        st.session_state["results"] = sorted(results, key=lambda r: (-r["coverage"], r["name"].casefold()))
        st.session_state["issues"] = issues
        st.session_state["snapshot"] = signature

for issue in st.session_state.get("issues", []):
    st.warning(issue)

results = st.session_state.get("results", [])
if results and st.session_state.get("snapshot") != signature:
    st.info("Inputs changed. Screen resumes again to update the results.")
elif results:
    st.divider()
    st.subheader("03 / Review your candidates")
    shortlisted = sum(bool(st.session_state.get("pick_" + row["id"])) for row in results)
    a, b, c = st.columns(3)
    a.metric("Resumes reviewed", len(results))
    b.metric("Average skill coverage", f'{sum(r["coverage"] for r in results) / len(results):.0f}%')
    c.metric("Shortlisted", shortlisted)
    st.caption("Review supporting text before making decisions. Matching checks literal terms and known aliases, not experience quality or negation.")
    f1, f2, f3 = st.columns([2, 2, 1])
    search = f1.text_input("Search filename", max_chars=200)
    minimum = f2.slider("Minimum skill coverage", 0, 100, 0)
    only_shortlist = f3.checkbox("Shortlisted only")
    visible = [r for r in results if search.casefold() in r["name"].casefold()
               and r["coverage"] >= minimum
               and (not only_shortlist or st.session_state.get("pick_" + r["id"], False))]
    if not visible:
        st.info("No candidates match these filters.")
    for rank, row in enumerate(results, start=1):
        if row not in visible:
            continue
        with st.container(border=True):
            title, score = st.columns([4, 1])
            title.write(f'**#{rank} · {row["name"]}**')
            score.metric("Skill coverage", f'{row["coverage"]:.0f}%')
            st.progress(row["coverage"] / 100)
            st.write("Matched: " + (", ".join(row["matched"]) or "None"))
            st.write("Missing: " + (", ".join(row["missing"]) or "None"))
            st.checkbox("Add to shortlist", key="pick_" + row["id"])
            with st.expander("View extracted resume text"):
                st.text(row["text"])
    export_rows = [{
        "Resume": r["name"], "Semantic similarity": "",
        "Skill coverage": r["coverage"], "Matched skills": r["matched"],
        "Missing skills": r["missing"],
        "Shortlisted": bool(st.session_state.get("pick_" + r["id"]))
    } for r in visible]
    st.download_button("Download filtered results · CSV", export_csv(export_rows),
                       "resume-studio-results.csv", "text/csv", disabled=not export_rows)
    st.caption("CSV includes the current filtered results and shortlist status. It excludes full resume text.")
else:
    st.divider()
    st.info("Your candidate review will appear here. Start with your own resumes or try the sample workspace.")
