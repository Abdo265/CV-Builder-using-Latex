import streamlit as st
import subprocess
import os
import tempfile
import shutil
import base64
import traceback
import shutil as sh

from models import (
    CV, PersonalInfo, Education, Experience, Course,
    Project, Certificate, Language, Volunteer,
    AdditionalExperience, TechSkillTopic, GradProj, PageOptions
)
from cv_builder import build_cv

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CV Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    body { font-family: 'Segoe UI', sans-serif; }

    .section-header {
        background: #f0f4ff;
        padding: 9px 16px;
        border-left: 4px solid #4f6ef7;
        border-radius: 0 6px 6px 0;
        margin: 24px 0 10px 0;
        font-weight: 700;
        font-size: 0.92rem;
        color: #1e293b;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .stButton > button { border-radius: 8px; }
    .stDownloadButton > button { border-radius: 8px; font-weight: 600; }
    .stDownloadButton > button:hover { background: #4f6ef7 !important; color: white !important; }
    .stAlert { border-radius: 8px; }

    .cv-preview-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 10px;
    }

    /* ── Live HTML CV ── */
    .cv-paper {
        background: white;
        border-radius: 6px;
        padding: 28px 32px;
        font-family: 'Times New Roman', serif;
        font-size: 10.5pt;
        color: #111;
        line-height: 1.35;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        max-height: 83vh;
        overflow-y: auto;
    }
    .cv-name { font-size: 20pt; font-weight: bold; text-align: center; margin-bottom: 4px; }
    .cv-contact {
        text-align: center;
        font-size: 7.8pt;
        color: #333;
        margin-bottom: 10px;
        line-height: 1.9;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .cv-contact a { color: #1a56db; text-decoration: none; }
    .cv-section-title {
        font-size: 10.5pt; font-weight: bold;
        text-transform: uppercase; letter-spacing: 0.06em;
        border-bottom: 1.2px solid #111;
        margin: 10px 0 4px 0;
        padding-bottom: 1px;
    }
    .cv-item-head {
        display: flex; justify-content: space-between;
        font-size: 9.5pt; font-weight: bold; margin-top: 4px;
    }
    .cv-item-sub {
        display: flex; justify-content: space-between;
        font-size: 8.5pt; font-style: italic; color: #333; margin-bottom: 2px;
    }
    .cv-bullet { font-size: 8.5pt; margin-left: 14px; margin-top: 1px; }
    .cv-bullet::before { content: "• "; }
    .cv-skills-row { font-size: 8.5pt; margin-bottom: 2px; }
    .cv-placeholder {
        text-align: center; color: #94a3b8;
        font-family: sans-serif; font-size: 13px;
        padding: 60px 20px;
    }
    .cv-objective { font-size: 9pt; color: #222; margin-bottom: 6px; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Sample data  (completely fake person)
# ─────────────────────────────────────────────
SAMPLE = {
    # ── Personal ──
    "name":      "Kareem Nabil Saber",
    "email":     "kareem.nabil@outlook.com",
    "phone":     "201123456789",
    "location":  "Alexandria, Egypt",
    "linkedin":  "https://linkedin.com/in/kareem-nabil",
    "github":    "https://github.com/kareem-nabil",
    "portfolio": "https://kareemnabil.me",
    "kaggle":    "https://kaggle.com/kareemnabil",
    "behance":   "",
    "career_subject": (
        "AI & Data Science graduate with hands-on experience in deep learning, NLP, "
        "and scalable backend systems. Passionate about turning raw data into "
        "intelligent products that solve real-world problems at scale."
    ),
    # ── Education ──
    "is_student":    "Graduate",
    "edu_title":     "Alexandria University",
    "edu_desc":      "B.Sc. Computer & Data Science",
    "edu_location":  "Alexandria, Egypt",
    "edu_date":      "2020 — 2024",
    "edu_materials": "Machine Learning, Deep Learning, NLP, Computer Vision, Big Data, Statistics",
    # ── Graduation Project ──
    "show_grad_proj":  True,
    "grad_proj_title": "Real-Time Arabic Sign Language Translator",
    "grad_proj_desc": (
        "Built a CNN-LSTM pipeline that translates Egyptian Arabic Sign Language gestures "
        "into text in real time with 93% accuracy on a custom 8,000-sample dataset. "
        "Deployed as a cross-platform mobile app reaching 1,200 beta users."
    ),
    "grad_proj_tech": "Python, PyTorch, OpenCV, Flutter, Firebase",
    # ── Work Experience ──
    "experiences": [
        {
            "title":    "Machine Learning Engineer",
            "date":     "Aug 2024 — Present",
            "location": "Instabug, Cairo",
            "desc": (
                "Built crash-prediction models reducing app ANR rate by 28% across 500+ client apps. "
                "Designed feature pipelines processing 4M+ daily SDK events using Apache Spark. "
                "Shipped a smart-tagging system that cut manual triage time by 40%."
            ),
        },
        {
            "title":    "Data Science Intern",
            "date":     "Jun 2023 — Aug 2023",
            "location": "Valeo Egypt, Cairo",
            "desc": (
                "Developed an anomaly detection system for automotive sensor data achieving 96% recall. "
                "Automated weekly reporting dashboards saving 8 engineer-hours per week."
            ),
        },
    ],
    # ── Courses ──
    "courses": [
        {
            "title":    "MLOps Specialization",
            "location": "Coursera — deeplearning.ai",
            "date":     "2023",
            "desc":     "CI/CD for ML, model monitoring, data drift detection, and automated retraining pipelines.",
        },
        {
            "title":    "Advanced SQL for Data Science",
            "location": "DataCamp",
            "date":     "2022",
            "desc":     "Window functions, CTEs, query optimization, and analytical SQL patterns on large datasets.",
        },
        {
            "title":    "Generative AI with LLMs",
            "location": "Coursera — AWS & deeplearning.ai",
            "date":     "2024",
            "desc":     "Transformer internals, fine-tuning strategies, RLHF, RAG pipelines, and LLM deployment.",
        },
    ],
    # ── Projects ──
    "projects": [
        {
            "title": "HealthScan AI",
            "desc": (
                "End-to-end diagnostic tool using Vision Transformers to detect 14 chest pathologies "
                "from X-rays. Achieved AUC 0.94 on the CheXpert benchmark. "
                "Wrapped as a HIPAA-friendly REST API serving 300+ radiologists in pilot."
            ),
            "urls": [
                ["GitHub",    "https://github.com/kareem-nabil/healthscan"],
                ["Live Demo", "https://healthscan.kareemnabil.me"],
            ],
        },
        {
            "title": "StockWise — Market Sentiment Engine",
            "desc": (
                "Fine-tuned FinBERT on 200k Arabic financial news articles integrated with live price feeds "
                "to generate daily buy/sell signals. Beat baseline ARIMA model by 18% in directional accuracy."
            ),
            "urls": [
                ["GitHub", "https://github.com/kareem-nabil/stockwise"],
                ["Dataset", "https://kaggle.com/kareemnabil/stockwise-dataset"],
            ],
        },
    ],
    # ── Volunteering ──
    "volunteers": [
        {
            "title": "AI Track Lead — Google Developer Student Club, Alexandria University",
            "date":  "2022 — 2024",
            "desc": (
                "Designed and delivered 15+ workshops on ML fundamentals and TensorFlow to 300+ students. "
                "Led a 48-hour hackathon attracting 120 participants and 8 industry sponsors."
            ),
            "urls": [["GDSC Page", "https://gdsc.community.dev/alexandria-university"]],
        },
    ],
    # ── Technical Skills ──
    "tech_skills": [
        {"title": "Languages",    "values": ["Python", "SQL", "Dart", "Bash"]},
        {"title": "ML / AI",      "values": ["PyTorch", "TensorFlow", "scikit-learn", "HuggingFace", "LangChain"]},
        {"title": "Data & MLOps", "values": ["Apache Spark", "MLflow", "Airflow", "DVC", "Weights & Biases"]},
        {"title": "Backend",      "values": ["FastAPI", "Django REST", "Docker", "PostgreSQL", "Redis"]},
        {"title": "Cloud",        "values": ["AWS (S3, EC2, SageMaker)", "GCP (BigQuery, Vertex AI)"]},
    ],
    # ── Soft Skills ──
    "soft_skills": "Critical Thinking, Public Speaking, Cross-functional Collaboration, Mentorship, Agile",
    # ── Certificates ──
    "certificates": [
        {
            "title":  "AWS Certified Machine Learning — Specialty",
            "date":   "Mar 2024",
            "desc":   "Validated expertise in designing, building, and deploying ML solutions on AWS.",
            "verify": "https://aws.amazon.com/verification",
        },
        {
            "title":  "Google Professional Data Engineer",
            "date":   "Nov 2023",
            "desc":   "Demonstrated ability to design and build data processing systems on GCP.",
            "verify": "https://cloud.google.com/certification",
        },
    ],
    # ── Additional Experience ──
    "additional_exp": [
        {
            "title": "Kaggle Competition — Top 4%",
            "desc":  "Ranked 87/2,300 in Bengali.AI Handwritten Grapheme Classification using multi-output CNNs with TTA.",
        },
        {
            "title": "Open Source — HuggingFace Hub",
            "desc":  "Published 3 fine-tuned Arabic NLP models with 1,200+ monthly downloads on the HuggingFace Model Hub.",
        },
    ],
    # ── Languages ──
    "langs": [
        {"language": "Arabic",  "level": "Native"},
        {"language": "English", "level": "C1 — Advanced (IELTS 7.5)"},
        {"language": "German",  "level": "A2 — Elementary"},
    ],
}


# ─────────────────────────────────────────────
#  Build a flat {widget_key: value} dict for sample
# ─────────────────────────────────────────────
def _build_sample_state() -> dict:
    s = SAMPLE
    st8: dict = {}

    # Personal
    st8["wi_name"]     = s["name"]
    st8["wi_email"]    = s["email"]
    st8["wi_phone"]    = s["phone"]
    st8["wi_location"] = s["location"]
    st8["wi_linkedin"] = s["linkedin"]
    st8["wi_github"]   = s["github"]
    st8["wi_portfolio"]= s["portfolio"]
    st8["wi_kaggle"]   = s["kaggle"]
    st8["wi_behance"]  = s["behance"]
    st8["wi_career"]   = s["career_subject"]

    # Education
    st8["wi_is_student"]    = s["is_student"]
    st8["wi_edu_title"]     = s["edu_title"]
    st8["wi_edu_desc"]      = s["edu_desc"]
    st8["wi_edu_location"]  = s["edu_location"]
    st8["wi_edu_date"]      = s["edu_date"]
    st8["wi_edu_materials"] = s["edu_materials"]

    # Section toggles
    st8["toggle_grad_proj"]      = s["show_grad_proj"]
    st8["toggle_experience"]     = True
    st8["toggle_courses"]        = True
    st8["toggle_projects"]       = True
    st8["toggle_volunteering"]   = True
    st8["toggle_certificates"]   = True
    st8["toggle_additional_exp"] = True

    # Grad Project
    st8["gp_title"] = s["grad_proj_title"]
    st8["gp_desc"]  = s["grad_proj_desc"]
    st8["gp_tech"]  = s["grad_proj_tech"]
    st8["gp_urls"]  = 1  # add_remove count

    # Experiences
    st8["exp_count"] = len(s["experiences"])
    for i, e in enumerate(s["experiences"]):
        st8[f"exp_title_{i}"] = e["title"]
        st8[f"exp_date_{i}"]  = e["date"]
        st8[f"exp_loc_{i}"]   = e["location"]
        st8[f"exp_desc_{i}"]  = e["desc"]

    # Courses
    st8["course_count"] = len(s["courses"])
    for i, c in enumerate(s["courses"]):
        st8[f"course_title_{i}"] = c["title"]
        st8[f"course_loc_{i}"]   = c["location"]
        st8[f"course_desc_{i}"]  = c["desc"]
        st8[f"course_date_{i}"]  = c["date"]

    # Projects
    st8["proj_count"] = len(s["projects"])
    for i, p in enumerate(s["projects"]):
        st8[f"proj_title_{i}"] = p["title"]
        st8[f"proj_desc_{i}"]  = p["desc"]
        urls = p.get("urls", [])
        st8[f"proj_links_{i}"] = max(1, len(urls))
        for j, u in enumerate(urls):
            st8[f"proj_lbl_{i}_{j}"] = u[0]
            st8[f"proj_url_{i}_{j}"] = u[1]

    # Volunteers
    st8["vol_count"] = len(s["volunteers"])
    for i, v in enumerate(s["volunteers"]):
        st8[f"vol_title_{i}"] = v["title"]
        st8[f"vol_date_{i}"]  = v["date"]
        st8[f"vol_desc_{i}"]  = v["desc"]

    # Tech Skills
    st8["skill_topics"] = len(s["tech_skills"])
    for i, sk in enumerate(s["tech_skills"]):
        st8[f"skill_title_{i}"] = sk["title"]
        st8[f"skill_vals_{i}"]  = ", ".join(sk["values"])

    # Soft Skills
    st8["wi_soft_skills"] = s["soft_skills"]

    # Certificates
    st8["cert_count"] = len(s["certificates"])
    for i, c in enumerate(s["certificates"]):
        st8[f"cert_title_{i}"]  = c["title"]
        st8[f"cert_date_{i}"]   = c["date"]
        st8[f"cert_desc_{i}"]   = c["desc"]
        st8[f"cert_verify_{i}"] = c["verify"]

    # Additional Exp
    st8["add_exp_count"] = len(s["additional_exp"])
    for i, a in enumerate(s["additional_exp"]):
        st8[f"add_title_{i}"] = a["title"]
        st8[f"add_desc_{i}"]  = a["desc"]

    # Languages
    st8["lang_count"] = len(s["langs"])
    for i, l in enumerate(s["langs"]):
        st8[f"lang_{i}"] = l["language"]
        st8[f"llvl_{i}"] = l["level"]

    return st8


def _clear_all_state():
    """Delete all widget keys so widgets revert to empty defaults."""
    prefixes = (
        "wi_", "gp_", "exp_", "course_", "proj_", "vol_",
        "skill_", "cert_", "add_", "lang_", "llvl_", "toggle_",
    )
    counts = ["exp_count","course_count","proj_count","vol_count",
              "skill_topics","cert_count","add_exp_count","lang_count","gp_urls"]
    for key in list(st.session_state.keys()):
        if any(key.startswith(p) for p in prefixes) or key in counts:
            del st.session_state[key]


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def sec(label: str):
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)


def section_toggle(key: str, label: str, default: bool = True) -> bool:
    col1, col2 = st.columns([8, 1])
    col1.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
    return col2.checkbox("Include", value=st.session_state.get(f"toggle_{key}", default),
                         key=f"toggle_{key}")


def add_remove(key: str, default: int = 1) -> int:
    if key not in st.session_state:
        st.session_state[key] = default
    c1, c2, _ = st.columns([1, 1, 6])
    if c1.button("➕", key=f"btn_add_{key}", use_container_width=True):
        st.session_state[key] += 1
    if c2.button("➖", key=f"btn_rem_{key}", use_container_width=True):
        if st.session_state[key] > 1:
            st.session_state[key] -= 1
    return st.session_state[key]


def check_pdflatex() -> bool:
    return sh.which("pdflatex") is not None


def render_pdf_iframe(pdf_bytes: bytes):
    b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="780px" '
        f'style="border:none; border-radius:8px;"></iframe>',
        unsafe_allow_html=True,
    )


def get_download_link(pdf_bytes: bytes, filename: str) -> str:
    b64 = base64.b64encode(pdf_bytes).decode()
    return (
        f'<a href="data:application/pdf;base64,{b64}" download="{filename}" '
        f'style="display:inline-flex;align-items:center;gap:6px;padding:9px 20px;'
        f'background:#4f6ef7;color:white;border-radius:8px;font-weight:600;'
        f'text-decoration:none;font-size:14px;">📥 Download PDF</a>'
    )


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ─────────────────────────────────────────────
#  Live HTML CV Preview
# ─────────────────────────────────────────────
def build_html_preview(data: dict) -> str:
    p = data
    parts = []

    # Header
    parts.append(f'<div class="cv-name">{esc(p["name"] or "Your Name")}</div>')

    contacts = []
    if p.get("location"):  contacts.append(f'📍 {esc(p["location"])}')
    if p.get("phone"):     contacts.append(f'📞 {esc(p["phone"])}')
    if p.get("email"):     contacts.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("linkedin"):  contacts.append(f'<a href="{esc(p["linkedin"])}">LinkedIn</a>')
    if p.get("github"):    contacts.append(f'<a href="{esc(p["github"])}">GitHub</a>')
    if p.get("kaggle"):    contacts.append(f'<a href="{esc(p["kaggle"])}">Kaggle</a>')
    if p.get("portfolio"): contacts.append(f'<a href="{esc(p["portfolio"])}">Portfolio</a>')
    if p.get("behance"):   contacts.append(f'<a href="{esc(p["behance"])}">Behance</a>')
    separator = ' <span style="color:#aaa">·</span> '
    parts.append(f'<div class="cv-contact">{separator.join(contacts)}</div>')

    # Objective
    if p.get("career_subject"):
        parts.append(f'<div class="cv-objective">{esc(p["career_subject"])}</div>')

    # Education
    if p.get("edu_title"):
        parts.append('<div class="cv-section-title">Education</div>')
        parts.append(f'<div class="cv-item-head"><span>{esc(p["edu_title"])}</span><span>{esc(p.get("edu_date",""))}</span></div>')
        parts.append(f'<div class="cv-item-sub"><span>{esc(p.get("edu_desc",""))}</span><span>{esc(p.get("edu_location",""))}</span></div>')
        if p.get("edu_materials"):
            parts.append(f'<div class="cv-bullet">Relevant Coursework: {esc(p["edu_materials"])}</div>')

    # Graduation Project
    gp = p.get("grad_proj", {})
    if gp and gp.get("title"):
        parts.append('<div class="cv-section-title">Graduation Project</div>')
        tech_str = " | ".join(gp.get("technologies", []))
        parts.append(f'<div class="cv-item-head"><span>{esc(gp["title"])}</span>'
                     f'<span style="font-weight:normal;font-style:italic">{esc(tech_str)}</span></div>')
        if gp.get("desc"):
            parts.append(f'<div class="cv-bullet">{esc(gp["desc"])}</div>')

    # Experience
    exps = [e for e in p.get("experiences", []) if e.get("title","").strip()]
    if exps:
        parts.append('<div class="cv-section-title">Work Experience</div>')
        for e in exps:
            parts.append(f'<div class="cv-item-head"><span>{esc(e["title"])}</span><span>{esc(e.get("date",""))}</span></div>')
            parts.append(f'<div class="cv-item-sub"><span>{esc(e.get("location",""))}</span></div>')
            if e.get("desc"):
                for line in e["desc"].split("."):
                    line = line.strip()
                    if line:
                        parts.append(f'<div class="cv-bullet">{esc(line)}.</div>')

    # Courses
    courses = [c for c in p.get("courses", []) if c.get("title","").strip()]
    if courses:
        parts.append('<div class="cv-section-title">Courses</div>')
        for c in courses:
            parts.append(f'<div class="cv-item-head"><span>{esc(c["title"])}</span><span>{esc(c.get("date",""))}</span></div>')
            parts.append(f'<div class="cv-item-sub"><span>{esc(c.get("location",""))}</span></div>')
            if c.get("desc"):
                parts.append(f'<div class="cv-bullet">{esc(c["desc"])}</div>')

    # Projects
    projs = [pr for pr in p.get("projects", []) if pr.get("title","").strip()]
    if projs:
        parts.append('<div class="cv-section-title">Projects</div>')
        for pr in projs:
            links = " | ".join(
                f'<a href="{esc(u[1])}">{esc(u[0])}</a>'
                for u in pr.get("urls",[]) if u[0] and u[1]
            )
            parts.append(f'<div class="cv-item-head"><span>{esc(pr["title"])}</span>'
                         f'<span style="font-weight:normal">{links}</span></div>')
            if pr.get("desc"):
                parts.append(f'<div class="cv-bullet">{esc(pr["desc"])}</div>')

    # Certificates
    certs = [c for c in p.get("certificates", []) if c.get("title","").strip()]
    if certs:
        parts.append('<div class="cv-section-title">Certificates</div>')
        for c in certs:
            verify = c.get("verify","").strip()
            verify_html = f' | <a href="{esc(verify)}">Verify</a>' if verify else ""
            parts.append(f'<div class="cv-item-head"><span>{esc(c["title"])}{verify_html}</span>'
                         f'<span>{esc(c.get("date",""))}</span></div>')
            if c.get("desc"):
                parts.append(f'<div class="cv-bullet">{esc(c["desc"])}</div>')

    # Tech Skills
    skills = [s for s in p.get("tech_skills", []) if s.get("title","").strip()]
    if skills:
        parts.append('<div class="cv-section-title">Technical Skills</div>')
        for s in skills:
            vals = ", ".join(s.get("values", []))
            parts.append(f'<div class="cv-skills-row"><strong>{esc(s["title"])}:</strong> {esc(vals)}</div>')

    # Soft Skills
    soft = p.get("soft_skills", [])
    if soft:
        parts.append(f'<div class="cv-skills-row"><strong>Soft Skills:</strong> {esc(", ".join(soft))}</div>')

    # Volunteering
    vols = [v for v in p.get("volunteers", []) if v.get("title","").strip()]
    if vols:
        parts.append('<div class="cv-section-title">Volunteering</div>')
        for v in vols:
            parts.append(f'<div class="cv-item-head"><span>{esc(v["title"])}</span><span>{esc(v.get("date",""))}</span></div>')
            if v.get("desc"):
                parts.append(f'<div class="cv-bullet">{esc(v["desc"])}</div>')

    # Additional Experience
    adds = [a for a in p.get("additional_exp", []) if a.get("title","").strip() or a.get("desc","").strip()]
    if adds:
        parts.append('<div class="cv-section-title">Additional Experience</div>')
        for a in adds:
            if a.get("title"):
                parts.append(f'<div class="cv-item-head"><span>{esc(a["title"])}</span></div>')
            if a.get("desc"):
                parts.append(f'<div class="cv-bullet">{esc(a["desc"])}</div>')

    # Languages
    langs = [l for l in p.get("langs", []) if l.get("language","").strip()]
    if langs:
        parts.append('<div class="cv-section-title">Languages</div>')
        lang_str = " · ".join(
            f'<strong>{esc(l["language"])}:</strong> {esc(l["level"])}'
            for l in langs
        )
        parts.append(f'<div class="cv-skills-row">{lang_str}</div>')

    return f'<div class="cv-paper">{"".join(parts)}</div>'


# ─────────────────────────────────────────────
#  pdflatex check
# ─────────────────────────────────────────────
pdflatex_available = check_pdflatex()

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown(
    "<h1 style='margin-bottom:0;font-size:1.8rem;color:#1e293b'>📄 CV Builder</h1>"
    "<p style='color:#64748b;margin-top:4px;margin-bottom:16px'>"
    "Fill the form — watch your CV take shape live on the right.</p>",
    unsafe_allow_html=True,
)

if not pdflatex_available:
    st.info(
        "ℹ️ **pdflatex not installed.** Download the `.tex` file and compile on "
        "[Overleaf](https://overleaf.com) (free) or install [MiKTeX](https://miktex.org).",
        icon="ℹ️",
    )

fill_mode = st.radio(
    "", ["✍️ Fill manually", "🧪 Load sample data"],
    horizontal=True, label_visibility="collapsed",
    key="fill_mode_radio",
)
use_sample = fill_mode == "🧪 Load sample data"
if use_sample:
    st.caption("📌 Pre-filled with a realistic sample — edit freely.")

# ── Detect mode change and reload session state ───────────────────────────────
if st.session_state.get("_prev_mode") != fill_mode:
    st.session_state["_prev_mode"] = fill_mode
    if use_sample:
        for k, v in _build_sample_state().items():
            st.session_state[k] = v
    else:
        _clear_all_state()
    st.rerun()

st.divider()

# ── Two-column layout ─────────────────────────────────────────────────────────
form_col, preview_col = st.columns([6, 5], gap="large")

with form_col:

    # ══════════════════════════════════════════
    #  1. Personal Info
    # ══════════════════════════════════════════
    sec("👤 Personal Information")
    c1, c2 = st.columns(2)
    name      = c1.text_input("Full Name *",                 key="wi_name",     placeholder="Ahmed Mohamed")
    email     = c2.text_input("Email *",                     key="wi_email",    placeholder="ahmed@email.com")
    phone     = c1.text_input("Phone (with country code) *", key="wi_phone",    placeholder="201012345678")
    location  = c2.text_input("Location *",                  key="wi_location", placeholder="Cairo, Egypt")
    linkedin  = c1.text_input("LinkedIn URL *",              key="wi_linkedin", placeholder="https://linkedin.com/in/...")
    github    = c2.text_input("GitHub URL *",                key="wi_github",   placeholder="https://github.com/...")
    portfolio = c1.text_input("Portfolio (optional)",        key="wi_portfolio",placeholder="https://yoursite.dev")
    kaggle    = c2.text_input("Kaggle (optional)",           key="wi_kaggle",   placeholder="https://kaggle.com/...")
    behance   = c1.text_input("Behance (optional)",          key="wi_behance",  placeholder="https://behance.net/...")
    career_subject = st.text_area(
        "Career Objective *", key="wi_career",
        placeholder="A passionate engineer with ...", height=85,
    )

    # ══════════════════════════════════════════
    #  2. Education
    # ══════════════════════════════════════════
    sec("🎓 Education")
    status_opts = ["Student (still enrolled)", "Graduate"]
    is_student = st.radio(
        "Status", status_opts,
        index=status_opts.index(st.session_state.get("wi_is_student", "Student (still enrolled)"))
              if st.session_state.get("wi_is_student") in status_opts else 0,
        horizontal=True, key="wi_is_student",
    )
    c1, c2 = st.columns(2)
    edu_title     = c1.text_input("University *",         key="wi_edu_title",     placeholder="Cairo University")
    edu_desc      = c2.text_input("Degree & Major *",     key="wi_edu_desc",      placeholder="B.Sc. Computer Science")
    edu_location  = c1.text_input("Location",             key="wi_edu_location",  placeholder="Cairo, Egypt")
    edu_date      = c2.text_input("Years",                key="wi_edu_date",      placeholder="2021 — 2025")
    edu_materials = st.text_input(
        "Key Courses (comma-separated)", key="wi_edu_materials",
        placeholder="Data Structures, Algorithms, ML",
    )

    # ══════════════════════════════════════════
    #  3. Graduation Project
    # ══════════════════════════════════════════
    show_grad_proj = False
    grad_proj_data = {}
    gp_label = "🏗️ Graduation Project" if is_student == "Graduate" else "🏗️ Graduation Project (optional)"
    show_grad = section_toggle("grad_proj", gp_label, default=(is_student == "Graduate"))
    if show_grad:
        show_grad_proj = True
        c1, c2 = st.columns(2)
        gp_title = c1.text_input("Project Title",  key="gp_title", placeholder="Smart Healthcare System")
        gp_desc  = st.text_area("Description",     key="gp_desc",  height=75, placeholder="An AI-powered system ...")
        gp_tech  = st.text_input("Technologies (comma-separated)", key="gp_tech", placeholder="Python, TensorFlow, React")
        n_gp_urls = add_remove("gp_urls", 1)
        gp_urls = []
        for i in range(n_gp_urls):
            gc1, gc2 = st.columns(2)
            lbl = gc1.text_input(f"Link #{i+1} Label", key=f"gp_url_lbl_{i}", placeholder="GitHub")
            url = gc2.text_input(f"Link #{i+1} URL",   key=f"gp_url_val_{i}", placeholder="https://github.com/...")
            if lbl and url:
                gp_urls.append([lbl, url])
        grad_proj_data = {"title": gp_title, "desc": gp_desc, "technologies": gp_tech, "urls": gp_urls}

    # ══════════════════════════════════════════
    #  4. Experience
    # ══════════════════════════════════════════
    show_exp = section_toggle("experience", "💼 Work Experience", default=True)
    experiences_data = []
    if show_exp:
        n_exp = add_remove("exp_count", 1)
        for i in range(n_exp):
            st.caption(f"Experience #{i+1}")
            c1, c2 = st.columns(2)
            t  = c1.text_input("Title / Role", key=f"exp_title_{i}", placeholder="Software Engineer")
            dt = c2.text_input("Date",         key=f"exp_date_{i}",  placeholder="Jan 2023 — Present")
            lo = c1.text_input("Location",     key=f"exp_loc_{i}",   placeholder="Cairo, Egypt")
            d  = st.text_area("Description",   key=f"exp_desc_{i}",  placeholder="Built ...", height=65)
            experiences_data.append({"title": t, "desc": d, "date": dt, "location": lo})
            if i < n_exp - 1:
                st.divider()

    # ══════════════════════════════════════════
    #  5. Courses
    # ══════════════════════════════════════════
    show_courses = section_toggle("courses", "📚 Courses", default=True)
    courses_data = []
    if show_courses:
        n_courses = add_remove("course_count", 1)
        for i in range(n_courses):
            st.caption(f"Course #{i+1}")
            c1, c2 = st.columns(2)
            t  = c1.text_input("Course Title", key=f"course_title_{i}", placeholder="Deep Learning Specialization")
            lo = c2.text_input("Platform",     key=f"course_loc_{i}",   placeholder="Coursera")
            d  = st.text_area("Description",   key=f"course_desc_{i}",  placeholder="Studied ...", height=55)
            dt = c1.text_input("Date",         key=f"course_date_{i}",  placeholder="2023")
            courses_data.append({"title": t, "desc": d, "location": lo, "date": dt, "skip": False})
            if i < n_courses - 1:
                st.divider()

    # ══════════════════════════════════════════
    #  6. Projects
    # ══════════════════════════════════════════
    show_projects = section_toggle("projects", "🚀 Projects", default=True)
    projects_data = []
    if show_projects:
        n_proj = add_remove("proj_count", 1)
        for i in range(n_proj):
            st.caption(f"Project #{i+1}")
            t = st.text_input("Project Title", key=f"proj_title_{i}", placeholder="E-commerce Platform")
            d = st.text_area("Description",    key=f"proj_desc_{i}",  placeholder="Built a full-stack ...", height=65)
            n_links = add_remove(f"proj_links_{i}", 1)
            urls = []
            for j in range(n_links):
                pc1, pc2 = st.columns(2)
                lbl = pc1.text_input("Link Label", key=f"proj_lbl_{i}_{j}", placeholder="GitHub")
                url = pc2.text_input("Link URL",   key=f"proj_url_{i}_{j}", placeholder="https://...")
                if lbl and url:
                    urls.append([lbl, url])
            projects_data.append({"title": t, "desc": d, "urls": urls, "skip": False})
            if i < n_proj - 1:
                st.divider()

    # ══════════════════════════════════════════
    #  7. Volunteering
    # ══════════════════════════════════════════
    show_vol = section_toggle("volunteering", "🤝 Volunteering", default=False)
    volunteers_data = []
    if show_vol:
        n_vol = add_remove("vol_count", 1)
        for i in range(n_vol):
            st.caption(f"Volunteer #{i+1}")
            c1, c2 = st.columns(2)
            t  = c1.text_input("Role / Organization", key=f"vol_title_{i}", placeholder="IEEE Student Branch")
            dt = c2.text_input("Date",                key=f"vol_date_{i}",  placeholder="2022 — Present")
            d  = st.text_area("Description",          key=f"vol_desc_{i}",  placeholder="Organized ...", height=60)
            volunteers_data.append({"title": t, "desc": d, "date": dt, "urls": []})
            if i < n_vol - 1:
                st.divider()

    # ══════════════════════════════════════════
    #  8. Technical Skills
    # ══════════════════════════════════════════
    sec("🛠️ Technical Skills")
    st.caption("Categories: Languages, Frameworks, Tools, Databases …")
    SKILL_SUGGESTIONS = {
        0: ("Languages",  "Python, C++, JavaScript, SQL"),
        1: ("Frameworks", "TensorFlow, React, FastAPI, Django"),
        2: ("Tools",      "Git, Docker, Linux, VS Code"),
        3: ("Databases",  "PostgreSQL, MongoDB, Redis"),
    }
    n_skill_topics = add_remove("skill_topics", 3)
    tech_skills_data = []
    for i in range(n_skill_topics):
        sugg_title = SKILL_SUGGESTIONS.get(i, ("", ""))[0]
        sugg_vals  = SKILL_SUGGESTIONS.get(i, ("", ""))[1]
        c1, c2 = st.columns([1, 3])
        title  = c1.text_input("Category", key=f"skill_title_{i}", placeholder=sugg_title)
        values = c2.text_input("Skills",   key=f"skill_vals_{i}",  placeholder=sugg_vals)
        if title and values:
            tech_skills_data.append({
                "title": title,
                "values": [v.strip() for v in values.split(",") if v.strip()],
            })

    # ══════════════════════════════════════════
    #  9. Soft Skills
    # ══════════════════════════════════════════
    sec("💡 Soft Skills")
    soft_skills_raw  = st.text_input(
        "Soft skills (comma-separated)", key="wi_soft_skills",
        placeholder="Problem Solving, Teamwork, Communication",
    )
    soft_skills_list = [s.strip() for s in soft_skills_raw.split(",") if s.strip()]

    # ══════════════════════════════════════════
    #  10. Certificates
    # ══════════════════════════════════════════
    show_certs = section_toggle("certificates", "🏆 Certificates", default=False)
    certificates_data = []
    if show_certs:
        n_certs = add_remove("cert_count", 1)
        for i in range(n_certs):
            st.caption(f"Certificate #{i+1}")
            c1, c2 = st.columns(2)
            t  = c1.text_input("Title",                key=f"cert_title_{i}",  placeholder="AWS Cloud Practitioner")
            dt = c2.text_input("Date",                 key=f"cert_date_{i}",   placeholder="Jan 2024")
            d  = st.text_area("Description",           key=f"cert_desc_{i}",   placeholder="Covered ...", height=55)
            v  = st.text_input("Verify URL (optional)", key=f"cert_verify_{i}", placeholder="https://...")
            certificates_data.append({"title": t, "desc": d, "date": dt, "verify": v.strip()})
            if i < n_certs - 1:
                st.divider()

    # ══════════════════════════════════════════
    #  11. Additional Experience
    # ══════════════════════════════════════════
    show_add = section_toggle("additional_exp", "📌 Additional Experience", default=False)
    additional_exp_data = []
    if show_add:
        n_add = add_remove("add_exp_count", 1)
        for i in range(n_add):
            st.caption(f"Item #{i+1}")
            t = st.text_input("Title",      key=f"add_title_{i}", placeholder="Open Source Contributor")
            d = st.text_area("Description", key=f"add_desc_{i}",  height=55, placeholder="Contributed to ...")
            if t.strip() or d.strip():
                additional_exp_data.append({"title": t.strip(), "desc": d.strip()})
            if i < n_add - 1:
                st.divider()

    # ══════════════════════════════════════════
    #  12. Languages
    # ══════════════════════════════════════════
    sec("🌍 Languages")
    n_langs = add_remove("lang_count", 2)
    langs_data = []
    for i in range(n_langs):
        c1, c2 = st.columns(2)
        lang  = c1.text_input("Language", key=f"lang_{i}", placeholder="English")
        level = c2.text_input("Level",    key=f"llvl_{i}", placeholder="C1 — Advanced")
        if lang and level:
            langs_data.append({"language": lang, "level": level})

    # ══════════════════════════════════════════
    #  Generate Button
    # ══════════════════════════════════════════
    st.divider()
    generate_clicked = st.button(
        "🚀 Generate CV  →  PDF + Download",
        type="primary", use_container_width=True,
    )

# ── RIGHT COLUMN: Live preview ────────────────────────────────────────────────
with preview_col:
    st.markdown('<div class="cv-preview-title">👁️ Live Preview</div>', unsafe_allow_html=True)

    preview_data = {
        "name": name, "email": email, "phone": phone, "location": location,
        "linkedin": linkedin, "github": github,
        "portfolio": portfolio or "",
        "kaggle": kaggle, "behance": behance,
        "career_subject": career_subject,
        "edu_title": edu_title, "edu_desc": edu_desc,
        "edu_location": edu_location, "edu_date": edu_date,
        "edu_materials": edu_materials,
        "grad_proj": {
            "title": grad_proj_data.get("title", "") if show_grad_proj else "",
            "desc":  grad_proj_data.get("desc",  "") if show_grad_proj else "",
            "technologies": [
                t.strip()
                for t in grad_proj_data.get("technologies", "").split(",")
                if t.strip()
            ] if show_grad_proj else [],
            "urls": grad_proj_data.get("urls", []) if show_grad_proj else [],
        },
        "experiences":    [e for e in experiences_data  if e.get("title","").strip()] if show_exp      else [],
        "courses":        [c for c in courses_data       if c.get("title","").strip()] if show_courses  else [],
        "projects":       [p for p in projects_data      if p.get("title","").strip()] if show_projects else [],
        "volunteers":     [v for v in volunteers_data    if v.get("title","").strip()] if show_vol      else [],
        "tech_skills":    tech_skills_data,
        "soft_skills":    soft_skills_list,
        "certificates":   [c for c in certificates_data  if c.get("title","").strip()],
        "additional_exp": additional_exp_data,
        "langs":          langs_data,
    }

    html_cv = build_html_preview(preview_data)
    st.markdown(html_cv, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Generate — runs below both columns
# ─────────────────────────────────────────────
if generate_clicked:
    errors = []
    if not name.strip():            errors.append("Full Name is required.")
    if not email.strip():           errors.append("Email is required.")
    if not phone.strip():           errors.append("Phone is required.")
    if not location.strip():        errors.append("Location is required.")
    if not linkedin.strip():        errors.append("LinkedIn URL is required.")
    if not github.strip():          errors.append("GitHub URL is required.")
    if not career_subject.strip():  errors.append("Career Objective is required.")
    if not edu_title.strip():       errors.append("University name is required.")
    if not edu_desc.strip():        errors.append("Degree & Major is required.")
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    with st.spinner("⚙️ Compiling your CV..."):
        try:
            personal = PersonalInfo.from_json({
                "name": name, "email": email, "phone": phone, "location": location,
                "linkedin": linkedin, "github": github,
                "portfolio": portfolio or behance or "", "kaggle": kaggle,
            })
            education = Education.from_json({
                "title": edu_title, "desc": edu_desc,
                "materials": edu_materials, "date": edu_date, "location": edu_location,
            })
            if show_grad_proj and grad_proj_data.get("title", "").strip():
                techs = [t.strip() for t in grad_proj_data.get("technologies", "").split(",") if t.strip()]
                grad_proj = GradProj.from_json({
                    "show": True, "title": grad_proj_data.get("title", ""),
                    "desc": grad_proj_data.get("desc", ""),
                    "technologies": techs, "urls": grad_proj_data.get("urls", []),
                })
            else:
                grad_proj = GradProj.from_json({"show": False, "title": "", "desc": "", "technologies": [], "urls": []})

            experiences  = [Experience.from_json(e)  for e in experiences_data  if e.get("title","").strip()]
            courses      = [Course.from_json(c)      for c in courses_data       if c.get("title","").strip()]
            projects     = [Project.from_json(p)     for p in projects_data      if p.get("title","").strip()]
            volunteers   = [Volunteer.from_json(v)   for v in volunteers_data    if v.get("title","").strip()]
            certificates = [Certificate.from_json({**c, "verify": c.get("verify","").strip()})
                            for c in certificates_data if c.get("title","").strip()]
            additional   = [AdditionalExperience.from_json(a) for a in additional_exp_data
                            if a.get("title","").strip() or a.get("desc","").strip()]
            langs        = [Language.from_json(l)    for l in langs_data         if l.get("language","").strip()]
            tech_skills  = [TechSkillTopic.from_json(t) for t in tech_skills_data]

            page_options = PageOptions.from_json({
                "items_spacing": -5, "top_margin": 30, "bottom_margin": 30,
                "right_margin": 40, "left_margin": 40,
                "section_pre_space": -4, "section_post_space": -4,
                "title_font_size": 20, "font_size": 10, "line_spacing": 12,
            })

            cv = CV(
                personal_info=personal, career_subject=career_subject,
                education=education, experiences=experiences, courses=courses,
                projects=projects, volunteers=volunteers, tech_skills=tech_skills,
                soft_skills=soft_skills_list, certificates=certificates,
                langs=langs, additional_experience=additional,
                page_options=page_options, grad_proj=grad_proj,
            )

            doc    = build_cv(cv)
            tmpdir = tempfile.mkdtemp()
            tex_path = os.path.join(tmpdir, "cv")
            doc.generate_tex(tex_path)
            tex_file = tex_path + ".tex"
            with open(tex_file, "r", encoding="utf-8") as f:
                tex_content = f.read()

            pdf_bytes = None
            if pdflatex_available:
                for _ in range(2):
                    subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", "cv.tex"],
                        cwd=tmpdir, capture_output=True, text=True,
                    )
                pdf_file = os.path.join(tmpdir, "cv.pdf")
                if os.path.exists(pdf_file):
                    with open(pdf_file, "rb") as f:
                        pdf_bytes = f.read()

            st.success("✅ CV generated successfully!")
            st.divider()

            safe_name = name.strip().replace(" ", "_")

            if pdf_bytes:
                dc1, dc2, dc3 = st.columns([2, 2, 3])
                dc1.download_button("📥 Download PDF", data=pdf_bytes,
                                    file_name=f"{safe_name}_CV.pdf", mime="application/pdf",
                                    use_container_width=True, type="primary")
                dc2.download_button("📄 Download .tex", data=tex_content.encode("utf-8"),
                                    file_name=f"{safe_name}_CV.tex", mime="text/plain",
                                    use_container_width=True)
                dc3.markdown(get_download_link(pdf_bytes, f"{safe_name}_CV.pdf"), unsafe_allow_html=True)

                st.markdown("### 👁️ PDF Preview")
                render_pdf_iframe(pdf_bytes)
            else:
                st.download_button("📄 Download .tex", data=tex_content.encode("utf-8"),
                                   file_name=f"{safe_name}_CV.tex", mime="text/plain",
                                   use_container_width=True)
                st.info("Upload the `.tex` to [Overleaf](https://overleaf.com) and click Recompile.", icon="ℹ️")

            with st.expander("📋 View / Copy LaTeX source"):
                st.code(tex_content, language="latex")

            shutil.rmtree(tmpdir, ignore_errors=True)

        except Exception as ex:
            st.error(f"Something went wrong: {ex}")
            with st.expander("🔍 Error details"):
                st.code(traceback.format_exc())

# ─────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:0.82rem;margin-top:4px'>"
    "Made with ❤️ by <strong style='color:#64748b'>Youseef</strong> &amp; "
    "<strong style='color:#64748b'>Abdelrahman</strong></p>",
    unsafe_allow_html=True,
)