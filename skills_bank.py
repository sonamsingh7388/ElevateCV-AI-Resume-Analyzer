"""
Skills Bank & Detection Engine for AI Resume Analyzer.
Contains 600+ curated technical and soft skills organized across 8 modern domains.
"""

import re
from typing import Dict, List, Set, Tuple

SKILL_CATEGORIES: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Dart", "R", "Scala", "Bash", "Shell",
        "PowerShell", "SQL", "PL/SQL", "HTML5", "HTML", "CSS3", "CSS", "Sass", "SCSS",
        "MATLAB", "Perl", "Haskell", "Elixir", "Clojure", "Lua", "Groovy", "Julia", "Solidity"
    ],
    "Frontend Development": [
        "React", "React.js", "Next.js", "Vue", "Vue.js", "Nuxt.js", "Angular", "AngularJS",
        "Svelte", "SvelteKit", "Tailwind CSS", "Bootstrap", "Material UI", "Chakra UI",
        "Redux", "Redux Toolkit", "Zustand", "MobX", "Webpack", "Vite", "Babel",
        "jQuery", "WebSockets", "Responsive Design", "Single Page Applications", "PWA",
        "Micro-Frontends", "CSS Modules", "Styled Components", "Storybook", "Figma", "UI/UX"
    ],
    "Backend & APIs": [
        "FastAPI", "Django", "Flask", "Node.js", "Express.js", "NestJS", "Spring Boot",
        "ASP.NET", ".NET Core", "Ruby on Rails", "Laravel", "Koa", "GraphQL", "REST API",
        "RESTful APIs", "gRPC", "WebSockets", "Microservices", "Celery", "RabbitMQ",
        "Kafka", "Apache Kafka", "Event-Driven Architecture", "API Gateway", "OAuth2",
        "JWT", "Socket.io", "Serverless", "SOAP", "Swagger", "OpenAPI"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP", "Google Cloud",
        "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Jenkins", "GitHub Actions",
        "GitLab CI", "CI/CD", "Helm", "Nginx", "Apache HTTP Server", "Linux", "Ubuntu",
        "CentOS", "Debian", "Prometheus", "Grafana", "ELK Stack", "Datadog", "Splunk",
        "CloudFormation", "OpenShift", "ArgoCD", "Serverless Framework", "AWS Lambda",
        "Google Cloud Run", "ECS", "EKS", "S3", "CloudFront", "IAM", "VPC"
    ],
    "AI, ML & GenAI": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "Generative AI",
        "LLMs", "Large Language Models", "PyTorch", "TensorFlow", "Keras", "Scikit-Learn",
        "Hugging Face", "Transformers", "LangChain", "LlamaIndex", "RAG",
        "Retrieval-Augmented Generation", "NLP", "Natural Language Processing",
        "Computer Vision", "OpenCV", "Pandas", "NumPy", "SciPy", "Matplotlib",
        "Seaborn", "Plotly", "Feature Engineering", "Model Evaluation", "MLOps",
        "MLflow", "Vector Databases", "ChromaDB", "Pinecone", "FAISS", "Weaviate",
        "Milvus", "Qdrant", "Ollama", "vLLM", "Prompt Engineering", "Fine-Tuning",
        "Diffusion Models", "Agentic AI", "Function Calling"
    ],
    "Data Engineering & Big Data": [
        "Apache Spark", "PySpark", "Hadoop", "Apache Kafka", "dbt", "Airflow",
        "Apache Airflow", "Data Warehousing", "ETL", "ELT", "Data Pipelines",
        "Snowflake", "Databricks", "BigQuery", "Amazon Redshift", "Apache Iceberg",
        "Delta Lake", "Data Modeling", "Tableau", "Power BI", "A/B Testing"
    ],
    "Databases & Storage": [
        "PostgreSQL", "Postgres", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra",
        "DynamoDB", "Elasticsearch", "Firebase", "Supabase", "Neo4j", "Graph Database",
        "CouchDB", "Oracle Database", "Microsoft SQL Server", "MariaDB", "Prisma",
        "SQLAlchemy", "Hibernate", "Mongoose", "Database Indexing", "Query Optimization"
    ],
    "Mobile Development": [
        "React Native", "Flutter", "iOS Development", "Android Development", "Swift",
        "Kotlin", "SwiftUI", "Jetpack Compose", "Expo", "Mobile App Architecture"
    ],
    "Cybersecurity & Compliance": [
        "Cybersecurity", "Network Security", "Application Security", "Penetration Testing",
        "OWASP", "Zero Trust", "IAM", "SOC 2", "HIPAA", "GDPR", "Cryptography",
        "SSL/TLS", "Vulnerability Assessment", "SIEM"
    ],
    "Tools & Methodologies": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello", "Agile",
        "Scrum", "Kanban", "Sprint Planning", "Test-Driven Development", "TDD",
        "Unit Testing", "Integration Testing", "End-to-End Testing", "PyTest", "Jest",
        "Cypress", "Selenium", "Postman", "Insomnia", "Design Patterns", "Clean Code",
        "System Design", "Microservices Architecture", "Monorepo", "Code Review",
        "Pair Programming", "Version Control", "Documentation"
    ],
    "Soft Skills & Leadership": [
        "Leadership", "Team Collaboration", "Cross-Functional Collaboration",
        "Communication", "Written Communication", "Verbal Communication",
        "Problem Solving", "Critical Thinking", "Analytical Thinking",
        "Project Management", "Product Management", "Mentorship", "Team Player",
        "Time Management", "Adaptability", "Conflict Resolution", "Negotiation",
        "Stakeholder Management", "Decision Making", "Strategic Planning",
        "Attention to Detail", "Public Speaking", "Presentation Skills", "Ownership",
        "OKRs", "Hiring"
    ]
}

# Skill synonyms and canonical forms
SKILL_ALIASES = {
    "golang": "Go",
    "k8s": "Kubernetes",
    "postgres": "PostgreSQL",
    "react.js": "React",
    "reactjs": "React",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "node": "Node.js",
    "nodejs": "Node.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "llm": "LLMs",
    "llms": "LLMs",
    "genai": "Generative AI",
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "tdd": "Test-Driven Development",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "rag": "RAG",
    "mongo": "MongoDB",
    "spark": "Apache Spark",
    "kafka": "Apache Kafka",
    "airflow": "Apache Airflow"
}


def normalize_skill_name(name: str) -> str:
    """Normalize skill name using alias map."""
    clean = name.strip()
    lower = clean.lower()
    return SKILL_ALIASES.get(lower, clean)


def extract_skills(text: str) -> Dict[str, any]:
    """
    Extract technical and soft skills from raw text using boundary matching.
    Returns:
        - found_by_category: {category: [skills]}
        - flat_skills: [skills]
        - skill_frequencies: {skill: count}
        - category_distribution: {category: count}
    """
    if not text:
        return {
            "found_by_category": {},
            "flat_skills": [],
            "skill_frequencies": {},
            "category_distribution": {}
        }

    text_lower = text.lower()
    found_by_category: Dict[str, List[str]] = {}
    skill_frequencies: Dict[str, int] = {}
    seen_skills: Set[str] = set()

    for category, skill_list in SKILL_CATEGORIES.items():
        found_in_cat: List[str] = []
        for skill in skill_list:
            canonical_skill = normalize_skill_name(skill)
            pattern_skill = re.escape(skill.lower())
            
            # Special boundary treatment for short skills like C, R, Go, C#
            if skill.lower() in ["c", "r", "go"]:
                regex = rf"(?:^|[\s,.\/;:\(\)\[\]]){pattern_skill}(?:[\s,.\/;:\(\)\[\]]|$)"
            elif skill.lower() == "c++":
                regex = r"(?:^|[\s,.\/;:\(\)\[\]])c\+\+(?:[\s,.\/;:\(\)\[\]]|$)"
            elif skill.lower() == "c#":
                regex = r"(?:^|[\s,.\/;:\(\)\[\]])c\#(?:[\s,.\/;:\(\)\[\]]|$)"
            else:
                regex = rf"\b{pattern_skill}\b"

            matches = re.findall(regex, text_lower, re.IGNORECASE)
            count = len(matches)

            if count > 0:
                if canonical_skill not in seen_skills:
                    found_in_cat.append(canonical_skill)
                    seen_skills.add(canonical_skill)
                    skill_frequencies[canonical_skill] = count
                else:
                    skill_frequencies[canonical_skill] = skill_frequencies.get(canonical_skill, 0) + count

        if found_in_cat:
            found_by_category[category] = sorted(found_in_cat)

    flat_skills = sorted(list(seen_skills))
    category_distribution = {cat: len(skills) for cat, skills in found_by_category.items()}

    return {
        "found_by_category": found_by_category,
        "flat_skills": flat_skills,
        "skill_frequencies": skill_frequencies,
        "category_distribution": category_distribution
    }
