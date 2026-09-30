"""Resume Studio API. Uploaded documents stay in memory."""
import hashlib
import logging
import os
from functools import lru_cache
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from screening import MAX_BYTES, SKILLS, chunks, extract_skills, extract_text, skill_comparison

app = FastAPI(title='Resume Studio', version='2.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[v.strip() for v in os.getenv('FRONTEND_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if v.strip()],
    allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['Content-Type'],
)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@app.get('/api/health')
def health():
    return {'status': 'ok'}

@app.get('/api/skills')
def skills():
    return {'skills': SKILLS}

@app.post('/api/suggest-skills')
def suggest_skills(job_description: str = Form(...)):
    if len(job_description) > 20000:
        raise HTTPException(400, 'Job description must be under 20,000 characters.')
    return {'skills': extract_skills(job_description)}

@app.post('/api/screen')
def screen(
    job_description: str = Form(...),
    required_skills: str = Form(''),
    method: str = Form('skills'),
    files: List[UploadFile] = File(...),
):
    try:
        if not job_description.strip() or len(job_description) > 20000:
            raise HTTPException(400, 'Enter a job description of 1–20,000 characters.')
        if method not in ['skills', 'semantic']:
            raise HTTPException(400, 'Choose skills or semantic comparison.')
        required = sorted({s.strip().lower() for s in required_skills.split(',') if s.strip()})
        if len(required) > 100 or any(len(s) > 80 for s in required):
            raise HTTPException(400, 'Use at most 100 skills, each under 80 characters.')
        if method == 'skills' and not required:
            raise HTTPException(400, 'Choose at least one required skill.')
        if not 1 <= len(files) <= 50:
            raise HTTPException(400, 'Upload 1–50 resumes.')
        rows, issues, seen = [], [], set()
        total = 0
        for upload in files:
            name = (upload.filename or 'resume').replace('\\', '/').rsplit('/', 1)[-1][:200]
            data = upload.file.read(MAX_BYTES + 1)
            total += len(data)
            if total > 50 * 1024 * 1024:
                raise HTTPException(413, 'Total uploaded content exceeds 50 MB. Use a smaller batch.')
            if len(data) > MAX_BYTES:
                issues.append({'file': name, 'message': 'File exceeds 10 MB.'})
                continue
            digest = hashlib.sha256(data).hexdigest()
            if digest in seen:
                issues.append({'file': name, 'message': 'Duplicate content skipped.'})
                continue
            seen.add(digest)
            try:
                text = extract_text(name, data)
                matched, missing, coverage = skill_comparison(text, required)
                rows.append({'id': digest, 'name': name, 'text': text,
                             'matched': matched, 'missing': missing,
                             'coverage': coverage, 'semantic': None})
            except Exception:
                issues.append({'file': name, 'message': 'Could not read text. Check format, encoding, file integrity, or use a text-based PDF.'})
        semantic_ready = False
        if rows and method == 'semantic':
            try:
                import numpy as np
                embedding_model = model()
                job_vectors = embedding_model.encode(chunks(job_description), normalize_embeddings=True)
                scores = []
                for row in rows:
                    vectors = embedding_model.encode(chunks(row['text']), normalize_embeddings=True)
                    scores.append(round(100 * float(np.max(job_vectors @ vectors.T, axis=1).mean()), 1))
                for row, score in zip(rows, scores):
                    row['semantic'] = score
                semantic_ready = True
            except Exception:
                logger.warning('Semantic comparison unavailable; using skill coverage.')
                issues.append({'file': None, 'message': 'Semantic comparison is unavailable. Results show skill coverage only. Install optional semantic dependencies and allow the first model download.'})
        key = 'semantic' if semantic_ready else 'coverage'
        rows.sort(key=lambda r: r[key] if r[key] is not None else -101, reverse=True)
        return {'candidates': rows, 'issues': issues, 'required': required,
                'method': 'semantic' if semantic_ready else 'skills'}
    finally:
        for upload in files:
            upload.file.close()
