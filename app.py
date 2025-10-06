import streamlit as st
import os
import tempfile
import docx2txt
from pdfminer.high_level import extract_text as pdf_extract
import pandas as pd
import re
import nltk
from sentence_transformers import SentenceTransformer, util

nltk.download('stopwords')

# --------------------------
# Helper Functions
# --------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text

def extract_text_from_file(file_path):
    if file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    elif file_path.endswith(".pdf"):
        return pdf_extract(file_path)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

skills_keywords = [
    "python", "java", "c++", "c#", "sql", "mysql", "postgresql", "mongodb",
    "html", "css", "javascript", "react", "angular", "node.js",
    "pandas", "numpy", "matplotlib", "seaborn",
    "machine learning", "deep learning", "nlp", "data science",
    "excel", "powerbi", "tableau", "git", "docker", "kubernetes"
]

def extract_skills(text, skills_list):
    found = []
    for skill in skills_list:
        if skill.lower() in text:
            found.append(skill)
    return list(set(found))

# --------------------------
# Streamlit UI
# --------------------------
st.title("📄 Resume Screening Automation")
st.markdown("Upload resumes + job description to get ranked candidates!")

# Job Description Input
job_description = st.text_area("Paste Job Description Here:")

# File Upload
uploaded_files = st.file_uploader("Upload Resumes (PDF/DOCX/TXT)", type=["pdf","docx","txt"], accept_multiple_files=True)

if st.button("Run Screening"):
    if job_description and uploaded_files:
        job_description_cleaned = clean_text(job_description)

        resumes_data = []

        # Save uploaded files to temp dir
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            text = extract_text_from_file(temp_path)
            text_cleaned = clean_text(text)
            skills = extract_skills(text_cleaned, skills_keywords)
            resumes_data.append({"Resume": uploaded_file.name, "Text": text_cleaned, "Skills": skills})

        # Load BERT model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Encode JD & resumes
        job_embed = model.encode(job_description_cleaned, convert_to_tensor=True)
        resume_embeds = model.encode([r["Text"] for r in resumes_data], convert_to_tensor=True)

        # Compute similarity
        cos_scores = util.cos_sim(job_embed, resume_embeds)[0].cpu().numpy()

        # Ranking
        for i, score in enumerate(cos_scores):
            resumes_data[i]["Match_Score"] = round(float(score), 3)

        ranking = pd.DataFrame(resumes_data).sort_values(by="Match_Score", ascending=False)

        # Show results
        st.subheader("🏆 Ranked Candidates")
        st.dataframe(ranking[["Resume", "Match_Score", "Skills"]])

        # Download CSV
        csv = ranking.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", csv, "resume_ranking.csv", "text/csv")

    else:
        st.warning("⚠️ Please enter a Job Description and upload resumes!")
