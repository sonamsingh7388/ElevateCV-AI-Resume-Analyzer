"""
Script to generate sample DOCX and PDF resumes for testing and demonstration.
"""

import os
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

os.makedirs("sample_resumes", exist_ok=True)

# 1. Generate DOCX Sample Resume: Alex Rivera (Senior Full Stack Engineer)
doc = Document()
doc.add_heading("ALEX RIVERA", level=0)
doc.add_paragraph("San Francisco, CA | (555) 382-9102 | alex.rivera@email.com | linkedin.com/in/alexrivera-dev | github.com/alexrivera")

doc.add_heading("PROFESSIONAL SUMMARY", level=1)
doc.add_paragraph(
    "Senior Full-Stack Engineer with 5+ years of experience designing and scaling high-availability microservices "
    "and responsive web applications. Expert in Python, FastAPI, TypeScript, React, PostgreSQL, and AWS. "
    "Demonstrated track record of reducing latency by 45% and leading engineering pods to on-time product releases."
)

doc.add_heading("TECHNICAL SKILLS", level=1)
doc.add_paragraph(
    "Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, Go\n"
    "Frontend: React, Next.js, Redux Toolkit, Tailwind CSS, Responsive Design\n"
    "Backend: FastAPI, Django, Node.js, Express.js, REST API, GraphQL, WebSockets\n"
    "Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, GitHub Actions, Terraform, Linux\n"
    "Databases: PostgreSQL, Redis, MongoDB, SQLAlchemy\n"
    "Methodologies: Agile, Scrum, TDD, Clean Architecture, System Design"
)

doc.add_heading("WORK EXPERIENCE", level=1)
p1 = doc.add_paragraph()
p1.add_run("Senior Software Engineer | NovaTech Solutions | San Francisco, CA\n").bold = True
p1.add_run("June 2022 - Present\n").italic = True
doc.add_paragraph("• Architected and deployed 14 high-throughput microservices using FastAPI and Docker, handling 18,000 requests/sec with 99.98% uptime.")
doc.add_paragraph("• Spearheaded database re-indexing and caching layer using Redis and PostgreSQL, slashing p99 API response times by 48%.")
doc.add_paragraph("• Built dynamic analytics dashboards in React and TypeScript, increasing active user engagement by 32% across 85,000 business accounts.")
doc.add_paragraph("• Mentored 5 junior engineers and established automated CI/CD deployment pipelines using GitHub Actions, cutting release cycles from 3 hours to 15 minutes.")

p2 = doc.add_paragraph()
p2.add_run("Software Engineer | CloudScale Systems | Austin, TX\n").bold = True
p2.add_run("August 2019 - May 2022\n").italic = True
doc.add_paragraph("• Engineered robust RESTful APIs in Django and Python that processed over $4.2M in annual recurring transactions.")
doc.add_paragraph("• Migrated legacy monolithic services to containerized Kubernetes deployments on AWS EKS, reducing cloud infrastructure spend by 28%.")
doc.add_paragraph("• Authored comprehensive unit and integration test suites with PyTest, elevating overall test coverage from 62% to 94%.")

doc.add_heading("KEY PROJECTS", level=1)
doc.add_paragraph("• PulseStream AI: Built a real-time analytics streaming engine using Python, WebSockets, and Redis, serving 50,000 events/minute.")
doc.add_paragraph("• DevSync: Developed a developer collaboration platform using Next.js, TypeScript, and PostgreSQL with 4,000+ GitHub stars.")

doc.add_heading("EDUCATION", level=1)
doc.add_paragraph("Bachelor of Science in Computer Science | University of Texas at Austin | Graduated 2019")

docx_path = os.path.join("sample_resumes", "sample_software_engineer.docx")
doc.save(docx_path)
print(f"Generated {docx_path}")


# 2. Generate PDF Sample Resume: Dr. Priya Sharma (Lead Data Scientist)
pdf_path = os.path.join("sample_resumes", "sample_data_scientist.pdf")
c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

c.setFont("Helvetica-Bold", 18)
c.drawString(50, height - 50, "PRIYA SHARMA, Ph.D.")

c.setFont("Helvetica", 9)
c.drawString(50, height - 68, "New York, NY | (212) 555-0194 | priya.sharma@mlresearch.io | linkedin.com/in/priyasharma-ds | github.com/priyasharma")

c.setStrokeColor(colors.HexColor("#4f46e5"))
c.setLineWidth(1.5)
c.line(50, height - 76, width - 50, height - 76)

y = height - 95
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "PROFESSIONAL SUMMARY")
y -= 14
c.setFont("Helvetica", 9.5)
summary_text = (
    "Lead Data Scientist and Machine Learning Researcher with 6+ years of experience delivering scalable AI solutions. "
    "Specialized in Deep Learning, Natural Language Processing, LLMs, PyTorch, and predictive analytics. "
    "Designed and deployed enterprise models resulting in $1.8M annual cost savings."
)
c.drawString(50, y, summary_text[:110])
y -= 12
c.drawString(50, y, summary_text[110:])

y -= 22
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "CORE COMPETENCIES & SKILLS")
y -= 14
c.setFont("Helvetica", 9)
c.drawString(50, y, "Languages & Querying: Python, SQL, R, Bash, C++")
y -= 12
c.drawString(50, y, "Machine Learning & AI: PyTorch, TensorFlow, Scikit-Learn, Deep Learning, NLP, Generative AI, LLMs, Transformers")
y -= 12
c.drawString(50, y, "Data & Pipelines: Pandas, NumPy, Apache Spark, BigQuery, Snowflake, Vector Databases, ChromaDB, ETL")
y -= 12
c.drawString(50, y, "MLOps & Cloud: Docker, Kubernetes, MLflow, AWS, GCP, CI/CD, Git, Linux")

y -= 22
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "PROFESSIONAL EXPERIENCE")

y -= 15
c.setFont("Helvetica-Bold", 10)
c.drawString(50, y, "Lead Data Scientist | Quantum Insights Corp | New York, NY")
c.setFont("Helvetica-Oblique", 9)
c.drawRightString(width - 50, y, "2021 - Present")
y -= 14
c.setFont("Helvetica", 9)
c.drawString(55, y, "• Architected and deployed an enterprise NLP classification engine using PyTorch and Transformers, achieving 94.6% F1-score.")
y -= 12
c.drawString(55, y, "• Spearheaded end-to-end MLOps pipeline migration with MLflow and Docker on AWS, reducing model retraining latency by 65%.")
y -= 12
c.drawString(55, y, "• Engineered customer lifetime value predictive models on BigQuery, directly driving an $850K revenue increase in Q3 2023.")
y -= 12
c.drawString(55, y, "• Led a team of 4 data scientists and machine learning engineers, mentoring on experimental design and A/B testing rigor.")

y -= 18
c.setFont("Helvetica-Bold", 10)
c.drawString(50, y, "Senior Machine Learning Engineer | DataVision Labs | Boston, MA")
c.setFont("Helvetica-Oblique", 9)
c.drawRightString(width - 50, y, "2018 - 2021")
y -= 14
c.setFont("Helvetica", 9)
c.drawString(55, y, "• Developed real-time anomaly detection pipelines processing over 25M daily transactions with Scikit-Learn and Apache Spark.")
y -= 12
c.drawString(55, y, "• Slashed false-positive fraud alerts by 38%, saving 250+ analyst review hours per month.")
y -= 12
c.drawString(55, y, "• Collaborated with engineering stakeholders to containerize models with Docker and integrate with production REST APIs.")

y -= 22
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "EDUCATION")
y -= 15
c.setFont("Helvetica-Bold", 9.5)
c.drawString(50, y, "Doctor of Philosophy (Ph.D.) in Machine Learning & Computer Science")
c.setFont("Helvetica", 9)
c.drawRightString(width - 50, y, "Graduated 2018")
y -= 12
c.drawString(50, y, "Columbia University | New York, NY")
y -= 14
c.setFont("Helvetica-Bold", 9.5)
c.drawString(50, y, "Bachelor of Science in Statistics and Mathematics")
c.setFont("Helvetica", 9)
c.drawRightString(width - 50, y, "Graduated 2014")
y -= 12
c.drawString(50, y, "Cornell University | Ithaca, NY")

c.showPage()
c.save()
print(f"Generated {pdf_path}")
