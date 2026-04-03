import streamlit as st
import PyPDF2
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Resume–JD Matcher", layout="wide")
st.title("📄 Resume vs Job Description Matcher")

# ---------------- UI ----------------
col1, col2 = st.columns(2)

with col1:
    jd_text = st.text_area("Paste Job Description", height=300)

with col2:
    resume_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# ---------------- TEXT CLEANING ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9+ ]', ' ', text)
    return text

# ---------------- EXPERIENCE EXTRACTION ----------------
def extract_experience(text):
    patterns = [
        r'(\d+)\+?\s+years',
        r'(\d+)\+?\s+yrs',
        r'(\d+)\+?\s+year'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return max([int(m) for m in matches])
    return 0

# ---------------- SKILL EQUIVALENTS DATABASE ----------------
SKILL_EQUIVALENTS = {

    # ================= PROGRAMMING =================
    "python": ["python", "python3", "scripting"],
    "java": ["java", "core java", "jdk"],
    "c": ["c language", "embedded c"],
    "cpp": ["c++", "cpp"],
    "javascript": ["javascript", "js"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "php": ["php"],
    "ruby": ["ruby"],
    "go": ["go", "golang"],

    # ================= DATA / AI / ML =================
    "machine learning": ["machine learning", "ml", "ml models"],
    "deep learning": ["deep learning", "dl", "neural networks"],
    "artificial intelligence": ["artificial intelligence", "ai"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "opencv", "image processing"],
    "data analysis": ["data analysis", "data analytics"],
    "data preprocessing": ["data preprocessing", "data cleaning"],

    # ================= LIBRARIES =================
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "opencv": ["opencv"],

    # ================= DATABASES =================
    "sql": ["sql", "mysql", "postgresql"],
    "nosql": ["nosql", "mongodb"],
    "dbms": ["dbms", "database management"],

    # ================= WEB / APIs =================
    "frontend development": ["frontend", "front end"],
    "backend development": ["backend", "server-side"],
    "full stack development": ["full stack"],
    "rest api": ["rest api", "api development"],
    "flask": ["flask"],
    "django": ["django"],
    "fastapi": ["fastapi"],
    "react": ["react", "reactjs"],
    "angular": ["angular"],

    # ================= CLOUD / DEVOPS =================
    "cloud computing": ["cloud", "cloud computing"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "deployment": ["deployment", "production"],
    "ci cd": ["ci cd", "continuous integration"],

    # ================= CYBERSECURITY =================
    "cybersecurity": ["cybersecurity", "information security"],
    "networking": ["networking", "computer networks"],
    "ethical hacking": ["ethical hacking"],
    "cryptography": ["cryptography", "encryption"],

    # ================= SOFT SKILLS =================
    "communication": ["communication", "verbal communication"],
    "teamwork": ["teamwork", "collaboration"],
    "leadership": ["leadership", "team lead"],
    "problem solving": ["problem solving", "analytical skills"],
    "time management": ["time management"],
    "critical thinking": ["critical thinking"]
}

# Reverse lookup map
KEYWORD_TO_SKILL = {}
for skill, variants in SKILL_EQUIVALENTS.items():
    for variant in variants:
        KEYWORD_TO_SKILL[variant] = skill

# ---------------- IMPROVED SKILL EXTRACTION ----------------
def extract_skills(text):
    found_skills = set()
    for keyword, skill in KEYWORD_TO_SKILL.items():
        if keyword in text:
            found_skills.add(skill)
    return found_skills

# ---------------- MAIN LOGIC ----------------
if st.button("🔍 Analyze Resume"):

    if not jd_text or not resume_file:
        st.warning("Please provide both Job Description and Resume PDF.")
    else:
        resume_text = extract_text_from_pdf(resume_file)

        jd_clean = clean_text(jd_text)
        resume_clean = clean_text(resume_text)

        # -------- SKILLS --------
        jd_skills = extract_skills(jd_clean)
        resume_skills = extract_skills(resume_clean)

        matched_skills = jd_skills & resume_skills
        missing_skills = jd_skills - resume_skills

        # -------- EXPERIENCE --------
        jd_exp = extract_experience(jd_clean)
        resume_exp = extract_experience(resume_clean)

        exp_match_score = min(resume_exp / jd_exp, 1) if jd_exp > 0 else 1
        skill_match_score = len(matched_skills) / len(jd_skills) if jd_skills else 1

        # -------- ATS SCORE --------
        ats_score = (0.7 * skill_match_score + 0.3 * exp_match_score) * 100

        # -------- DISPLAY --------
        colA, colB = st.columns(2)

        with colA:
            st.subheader("✅ Matched Skills")
            if matched_skills:
                for s in sorted(matched_skills):
                    st.write(f"- {s}")
            else:
                st.info("No skills matched")

        with colB:
            st.subheader("❌ Missing Skills")
            if missing_skills:
                for s in sorted(missing_skills):
                    st.write(f"- {s}")
            else:
                st.success("No major skills missing 🎉")

        st.subheader("💼 Experience Analysis")
        st.write(f"**Required Experience (JD):** {jd_exp} years")
        st.write(f"**Your Experience:** {resume_exp} years")

        if resume_exp >= jd_exp:
            st.success("Experience requirement satisfied ✅")
        else:
            st.warning("Experience requirement not fully met ⚠")

        st.subheader("📊 Expected ATS Score")
        st.progress(int(ats_score))
        st.success(f"Expected ATS Score: {round(ats_score, 2)} / 100")
