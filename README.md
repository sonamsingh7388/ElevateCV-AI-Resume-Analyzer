# 🎯 ElevateCV — Advanced AI Resume Analyzer & ATS Optimization Engine

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Google%20GenAI-Gemini%20Flash-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, comprehensive AI-powered resume analyzer, ATS (Applicant Tracking System) intelligence platform, live resume optimization studio, and career collateral suite. ElevateCV extracts, analyzes, benchmarks, transforms, and exports resumes against modern recruitment standards and targeted job descriptions.

---

## ✨ Key Features & Capabilities

### 1. 📄 Multi-Format Document Ingestion
- High-fidelity text extraction from **PDF** (via `pypdf`), **Word DOCX** (via `python-docx`), and **Plain Text (TXT)**.
- Automated error recovery for password-protected, scanned, or malformed files.
- Document metrics auditing: word count pacing, estimated recruiter read time, and section completeness.

### 2. 🎯 Enterprise ATS Scoring Engine (0-100)
Evaluates 5 core ATS dimensions with weighted breakdowns and actionable feedback:
- 🏗️ **Structure & Formatting (20%)**: Contact information completeness, standard heading hierarchy, and ATS parseability.
- 🔍 **Skill Breadth & Density (25%)**: 800+ industry skills across 10 distinct technical and soft skill domains.
- 📊 **Quantified Impact & Metrics (20%)**: Detects percentages, dollar figures, user scale, latency improvements, and KPI milestones.
- 🗣️ **Action Verbs & Voice (20%)**: Identifies proactive power verbs while penalizing passive clichés.
- 📄 **Brevity & Balance (15%)**: Optimal word density and layout balance.

### 3. 🔍 Skills Intelligence & Live Filter
- Broad taxonomies across **10 Domains**: Programming Languages, Frontend, Backend, Cloud & DevOps, AI/ML & GenAI, Data Engineering, Databases, Mobile Development, Cybersecurity & Compliance, and Soft Skills.
- Real-time search filter to locate specific competencies.
- Interactive domain distribution bar charts and frequency rankings.

### 4. 💼 Job Description Fit & Interactive Score Simulator
- Real-time TF-IDF n-gram and Cosine Similarity comparison between resume and target JD.
- Color-coded matching skills (emerald badges) vs missing critical keywords (rose badges).
- **Interactive Keyword Simulator**: Select missing skills to simulate an updated ATS score and Job Match score in real time.
- Contextual keyword integration blueprint explaining how to naturally embed missing skills.

### 5. 🚀 Dynamic Google XYZ Formula Bullet Rewriter
- Transforms passive bullets into Google's benchmark: *"Accomplished [X] as measured by [Y] by doing [Z]"*.
- Generates 3 distinct multi-style upgrades:
  1. **Performance & Scale Variant** (throughput, latency, concurrency, user volume)
  2. **Leadership & System Architecture Variant** (technical decisions, ownership, mentoring)
  3. **Business Value & Cost Reduction Variant** (ROI, savings, delivery velocity)
- Supports live Gemini generation and zero-friction offline heuristic NLP intelligence.

### 6. 📄 Live ATS Resume Studio & DOCX Generator
- Interactive section-by-section live editor (Summary, Technical Skills, Experience, Projects, Education).
- **One-Click Auto-Optimizer**: Replaces weak verbs with power verbs, injects missing job keywords, and formats bullets cleanly.
- **Export to Microsoft Word (.docx)** with 0.75-inch ATS margins, Calibri typography, and clean headings.
- **Export to Markdown (.md)** for digital applications.

### 7. ✉️ Tailored Cover Letter & Recruiter Pitch Generator
- Generates a customized 300-word Executive Cover Letter and a punchy 150-word LinkedIn InMail outreach message.
- Dynamically aligns candidate achievements with company name and target role.
- One-click export to **Word Document (.docx)**.

### 8. 👥 Multi-Candidate Benchmarking & Leaderboard (Recruiter Mode)
- Evaluates candidate resumes side-by-side against target job requirements.
- Side-by-side competitive leaderboard highlighting Top Role Fit Leader and Top ATS Score Leader.
- Grouped Plotly comparison bar charts and multi-radar balance overlays.

### 9. 🤖 Deep AI Critique & STAR Interview Prep
- Executive recruiter critique: First Impression, Standout Strengths, Red Flags, Bullet Rewrites.
- STAR-Method behavioral and technical interview questions with model answers.
- One-click download of the complete **Comprehensive ATS & AI Audit Report (Markdown)**.

---

## 📁 Project Architecture

```
resume anlyzer/
├── .env.example                # Sample environment template for GEMINI_API_KEY
├── .gitignore                  # Git ignore rules for Python, cache, and secrets
├── requirements.txt            # Project dependencies
├── README.md                   # Complete system documentation
├── app.py                      # Main Streamlit web application & 8-tab studio
├── test_app.py                 # Comprehensive unit & integration test suite (13 tests)
├── generate_samples.py         # Test resume generator script
├── assets/
│   └── style.css               # Modern glassmorphism CSS design system
├── modules/
│   ├── __init__.py
│   ├── parser.py               # Robust PDF & DOCX text extraction & section segmentation
│   ├── skills_bank.py          # 800+ curated skills across 10 modern domains
│   ├── analyzer.py             # Contact extraction, metrics, verbs, and structure audit
│   ├── scorer.py               # Multi-factor ATS scoring algorithm (0-100)
│   ├── matcher.py              # TF-IDF cosine similarity & job description gap matcher
│   ├── suggestions.py          # Action verb upgrades & XYZ formula transformation
│   ├── resume_generator.py     # Section auto-optimizer & ATS DOCX document exporter
│   ├── cover_letter.py         # Custom cover letter generator & DOCX exporter
│   ├── comparator.py           # Multi-candidate competitive ranking & comparison
│   ├── gemini_client.py        # Gemini SDK integration with automatic offline fallback
│   └── charts.py               # Plotly gauge, radar, horizontal bar, and comparative charts
└── sample_resumes/
    ├── sample_software_engineer.docx
    ├── sample_software_engineer.txt
    ├── sample_data_scientist.pdf
    └── sample_data_scientist.txt
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- `pip` package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key
To enable live Gemini generation, set your API key in an `.env` file or environment variable:
```bash
# Copy template
cp .env.example .env

# Edit .env and enter your key:
GEMINI_API_KEY="your_actual_gemini_api_key_here"
```
> **Note**: You can also enter the Gemini API key directly in the application's sidebar with password masking, or simply run the app without any key—it will seamlessly use the built-in intelligent heuristic engine!

---

## 💻 Running the Application

Launch the Streamlit app with:

```bash
streamlit run app.py
```

The web application will open in your default browser at:
**`http://localhost:8501`**

---

## 🧪 Running Automated Tests

Run the full end-to-end test suite:

```bash
python test_app.py
```

All 13 integration and unit tests will run and validate parser reliability, skills bank extraction, ATS scoring, job matching, dynamic bullet transformations, DOCX document generation, cover letter creation, and multi-candidate comparisons.
