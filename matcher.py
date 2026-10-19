"""
Resume vs Job Description Matcher.
Performs TF-IDF n-gram cosine similarity, skill overlap analysis,
and extracts matching skills and missing target keywords.
"""

import math
import re
from typing import Dict, List, Set, Any, Tuple
from modules.skills_bank import extract_skills

# Common English stop words
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

PRESET_JOB_DESCRIPTIONS = {
    "Senior Full-Stack AI Engineer": """
We are seeking an experienced Senior Full-Stack AI Engineer to architect, build, and deploy high-performance applications.
Requirements:
- 4+ years building production web apps with Python, FastAPI, Django, and Node.js.
- Frontend proficiency in React, TypeScript, Next.js, and Tailwind CSS.
- Hands-on experience with Generative AI, LLMs, LangChain, RAG pipelines, PyTorch, and OpenAI / Gemini APIs.
- Deep expertise in PostgreSQL, Redis, Docker, Kubernetes, and AWS or GCP cloud infrastructure.
- Strong knowledge of CI/CD, Git, automated testing (PyTest, Jest), and microservices architecture.
- Excellent communication, team leadership, problem-solving, and agile development skills.
    """.strip(),

    "Senior Data Scientist / ML Engineer": """
Looking for a Senior Data Scientist / Machine Learning Engineer to drive data-informed solutions.
Requirements:
- Solid background in Machine Learning, Deep Learning, NLP, and Statistical Modeling.
- Expert proficiency in Python, PyTorch, TensorFlow, Scikit-Learn, Pandas, and NumPy.
- Production MLOps experience with MLflow, Docker, Kubernetes, and Vector Databases (Pinecone, ChromaDB).
- Experience working with BigQuery, Snowflake, SQL, and building scalable ETL data pipelines.
- Track record of delivering measurable business impact through A/B testing and predictive modeling.
- Master's or Bachelor's in Computer Science, Data Science, or related quantitative field.
    """.strip(),

    "Cloud DevOps & Platform Engineer": """
We are hiring a Cloud DevOps & Platform Engineer to automate and scale our cloud infrastructure.
Requirements:
- 3+ years managing multi-region cloud systems on AWS or Azure using Terraform and Ansible.
- Strong containerization expertise with Docker, Kubernetes (K8s), Helm, and ArgoCD.
- Proven experience designing and managing robust CI/CD pipelines via GitHub Actions and GitLab CI.
- Infrastructure monitoring with Prometheus, Grafana, and ELK Stack.
- Proficiency in Linux system administration, Shell/Bash scripting, and Python automation.
- Deep understanding of cloud security, IAM policies, networking (VPC, DNS, Load Balancers).
    """.strip(),

    "Senior Frontend Engineer (React/TypeScript)": """
We are looking for a Senior Frontend Engineer passionate about crafting beautiful, intuitive user experiences.
Requirements:
- 4+ years of professional web development using JavaScript (ES6+), TypeScript, React, and Next.js.
- Mastery of responsive design, CSS3, Tailwind CSS, styled-components, and modern UI libraries.
- State management with Redux Toolkit or Zustand, and client-side data fetching via GraphQL or REST.
- Experience with testing suites (Jest, React Testing Library, Cypress) and performance profiling.
- Strong familiarity with Webpack, Vite, CI/CD, and Git workflows.
- High attention to UI/UX detail and collaboration with Figma design teams.
    """.strip()
}


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alpha words and bigrams, filtering stop words."""
    cleaned = re.sub(r"[^a-zA-Z0-9\+\#\.]", " ", text.lower())
    words = [w for w in cleaned.split() if len(w) > 1 and w not in STOP_WORDS]
    
    # Also generate bigrams
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    return words + bigrams


def compute_tf_idf_similarity(doc1: str, doc2: str) -> float:
    """
    Computes Cosine Similarity between doc1 and doc2 using TF-IDF vectors.
    Returns float between 0.0 and 1.0.
    """
    if not doc1.strip() or not doc2.strip():
        return 0.0

    tokens1 = _tokenize(doc1)
    tokens2 = _tokenize(doc2)

    if not tokens1 or not tokens2:
        return 0.0

    # Build vocabulary
    vocab = sorted(list(set(tokens1 + tokens2)))
    num_docs = 2

    # Term counts
    count1 = {}
    for t in tokens1:
        count1[t] = count1.get(t, 0) + 1

    count2 = {}
    for t in tokens2:
        count2[t] = count2.get(t, 0) + 1

    # IDF calculation
    vec1 = []
    vec2 = []
    for term in vocab:
        df = (1 if term in count1 else 0) + (1 if term in count2 else 0)
        idf = math.log((1 + num_docs) / (1 + df)) + 1.0

        tf1 = count1.get(term, 0) / len(tokens1)
        tf2 = count2.get(term, 0) / len(tokens2)

        vec1.append(tf1 * idf)
        vec2.append(tf2 * idf)

    # Cosine Similarity: dot(v1, v2) / (norm(v1) * norm(v2))
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    sim = dot / (norm1 * norm2)
    return max(0.0, min(1.0, sim))


def compare_resume_to_job(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Comprehensive match analysis between Resume and Job Description.
    Calculates:
        - Overall Match Score %
        - Matching Skills
        - Missing Target Skills
        - Match Category Breakdown
        - Keyword Relevance
    """
    if not resume_text.strip() or not jd_text.strip():
        return {
            "match_score": 0.0,
            "semantic_similarity": 0.0,
            "skill_match_ratio": 0.0,
            "matching_skills": [],
            "missing_skills": [],
            "extra_skills": [],
            "jd_skills": [],
            "resume_skills": []
        }

    # Extract skills from both documents
    resume_skills_info = extract_skills(resume_text)
    jd_skills_info = extract_skills(jd_text)

    resume_skills_set = set(resume_skills_info.get("flat_skills", []))
    jd_skills_set = set(jd_skills_info.get("flat_skills", []))

    matching_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
    missing_skills = sorted(list(jd_skills_set - resume_skills_set))
    extra_skills = sorted(list(resume_skills_set - jd_skills_set))

    # Skill match ratio
    if len(jd_skills_set) > 0:
        skill_ratio = len(matching_skills) / len(jd_skills_set)
    else:
        skill_ratio = 1.0 if len(resume_skills_set) > 0 else 0.5

    # Semantic similarity
    semantic_sim = compute_tf_idf_similarity(resume_text, jd_text)

    # Composite Match Score: 55% skill match + 45% semantic context match
    composite_score = (skill_ratio * 0.55 + semantic_sim * 0.45) * 100
    # Apply reasonable boost if majority of critical skills are present
    if skill_ratio > 0.7:
        composite_score = min(100.0, composite_score + 5.0)

    composite_score = round(max(0.0, min(100.0, composite_score)), 1)

    return {
        "match_score": composite_score,
        "semantic_similarity": round(semantic_sim * 100, 1),
        "skill_match_ratio": round(skill_ratio * 100, 1),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "jd_skills": sorted(list(jd_skills_set)),
        "resume_skills": sorted(list(resume_skills_set))
    }
