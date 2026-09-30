"""File extraction and auditable skill coverage; independent of the UI."""
import csv
import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

SKILLS = ['python', 'java', 'c++', 'c#', 'sql', 'mysql', 'postgresql', 'mongodb',
          'html', 'css', 'javascript', 'typescript', 'react', 'angular', 'node.js',
          'fastapi', 'flask', 'django', 'pandas', 'numpy', 'machine learning',
          'deep learning', 'nlp', 'data science', 'excel', 'power bi', 'tableau',
          'git', 'docker', 'kubernetes', 'aws', 'azure', 'linux', 'rest api']
ALIASES = {'node.js': ['nodejs', 'node js'], 'power bi': ['powerbi'],
           'postgresql': ['postgres'], 'javascript': ['js'],
           'typescript': ['ts'], 'rest api': ['rest apis', 'restful api'],
           'nlp': ['natural language processing']}
MAX_BYTES = 10 * 1024 * 1024

def extract_text(name, data):
    if not data or len(data) > MAX_BYTES:
        raise ValueError('Upload a nonempty file smaller than 10 MB.')
    suffix = Path(name).suffix.lower()
    if suffix == '.txt':
        text = data.decode('utf-8-sig')
    elif suffix == '.pdf':
        from pdfminer.high_level import extract_text as pdf_extract
        text = pdf_extract(io.BytesIO(data))
    elif suffix == '.docx':
        with zipfile.ZipFile(io.BytesIO(data)) as document:
            info = document.getinfo('word/document.xml')
            if info.file_size > 20 * 1024 * 1024:
                raise ValueError('Document contents are too large.')
            root = ElementTree.fromstring(document.read(info))
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            text = '\n'.join(' '.join(t.text or '' for t in p.findall('.//w:t', ns))
                             for p in root.findall('.//w:p', ns))
    else:
        raise ValueError('Supported formats: PDF, DOCX, TXT.')
    if not text.strip():
        raise ValueError('No readable text found. Scanned PDFs need OCR first.')
    if len(text) > 200000:
        raise ValueError('Extracted text exceeds 200,000 characters.')
    return text

def has_skill(text, skill):
    return any(re.search(r'(?<![\w+#])' + re.escape(term) + r'(?![\w+#])',
                         text, re.IGNORECASE)
               for term in [skill] + ALIASES.get(skill, []))

def extract_skills(text, skills=SKILLS):
    return sorted({s for s in skills if has_skill(text, s)})

def skill_comparison(text, required):
    matched = extract_skills(text, required)
    missing = sorted(set(required) - set(matched))
    return matched, missing, round(100 * len(matched) / len(required), 1) if required else None

def chunks(text, words=160):
    tokens = text.split()
    return [' '.join(tokens[i:i + words]) for i in range(0, len(tokens), words)]

def export_csv(rows):
    output = io.StringIO()
    fields = ['Resume', 'Semantic similarity', 'Skill coverage', 'Matched skills', 'Missing skills', 'Shortlisted']
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        safe = {}
        for field in fields:
            value = row.get(field, '')
            if isinstance(value, list):
                value = ', '.join(value)
            if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
                value = "'" + value
            safe[field] = value
        writer.writerow(safe)
    return output.getvalue().encode('utf-8-sig')
