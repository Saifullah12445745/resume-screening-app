Resume Screening Automation
Project Overview

This project automates the process of resume filtering and candidate ranking by matching resumes against a given Job Description (JD).
It leverages BERT embeddings for semantic similarity and also extracts skills from resumes.

The app is built with Streamlit and provides an easy-to-use web interface where you can:

Paste a Job Description

Upload multiple resumes (PDF, DOCX, TXT)

Extract skills from each resume

Rank resumes based on similarity with the JD

Download results as a CSV file
## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  npm install
```

Start the server

```bash
  npm run start
```


## Roadmap

- Additional browser support

- Add more integrations


## Related

Here are some related projects

[Awesome README](https://github.com/matiassingers/awesome-readme)


![Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th5xamgrr6se0x5ro4g6.png)


## Key Features
✅ Upload resumes in multiple formats (PDF, DOCX, TXT)
✅ Extract skills from resumes using a keyword dictionary
✅ Match resumes to job descriptions using BERT (Sentence Transformers)
✅ Rank candidates based on semantic similarity
✅ Interactive Streamlit UI
✅ Export ranked results to CSV
✅ Deployment-ready on Streamlit Cloud


## Tech Stack
Python 3.8+

Streamlit
 – Web UI

Sentence Transformers
 – BERT embeddings

NLTK
 – Stopwords & text preprocessing

docx2txt
 – Extract text from .docx

pdfminer.six
 – Extract text from .pdf

Pandas
 – Data handling
## Project Structure
resume-screening-app/
│── app.py              # Main Streamlit app
│── requirements.txt    # Python dependencies
│── README.md           # Project documentation
│── resumes/            # (Optional) sample resumes for testing

## Installation & Setup
1 Clone the repository
git clone https://github.com/your-username/resume-screening-app.git
cd resume-screening-app

2️ Install dependencies
pip install -r requirements.txt

3️ Run the app
streamlit run app.py

The app will open in your browser at:
👉 http://localhost:8501