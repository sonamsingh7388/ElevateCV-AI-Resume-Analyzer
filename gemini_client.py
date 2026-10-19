"""
Gemini API Client for AI Resume Analyzer.
Integrates with Google GenAI SDK using secure environment variable
or session key management, with a comprehensive offline heuristic fallback.
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

# Prioritized list of model candidates for maximum compatibility
CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-3.8-flash"
]


def get_resolved_api_key(provided_key: Optional[str] = None) -> Optional[str]:
    """Retrieve API key from explicit input, environment variable, or secrets."""
    if provided_key and provided_key.strip():
        return provided_key.strip()
    return os.getenv("GEMINI_API_KEY", "").strip() or None


def is_gemini_available(api_key: Optional[str] = None) -> bool:
    """Check if a valid Gemini API key is configured."""
    key = get_resolved_api_key(api_key)
    return bool(key and len(key) >= 15)


def _call_gemini_with_fallback(client, prompt: str) -> Tuple[str, str]:
    """Helper to try models in sequence until one succeeds."""
    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            text = getattr(resp, "text", "") or ""
            if text.strip():
                return text.strip(), model_name
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"All candidate Gemini models failed. Last error: {last_err}")



def generate_gemini_critique(
    resume_text: str,
    jd_text: Optional[str] = None,
    api_key: Optional[str] = None,
    offline_fallback_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate deep executive critique and personalized bullet rewrites.
    Uses Google GenAI SDK if key is available; otherwise provides structured offline fallback.
    """
    key = get_resolved_api_key(api_key)

    if not key:
        return _build_offline_fallback(resume_text, jd_text, offline_fallback_data, reason="No API key provided")

    try:
        from google import genai
        client = genai.Client(api_key=key)

        prompt = f"""
You are an elite Fortune 500 Executive Recruiter and ATS Optimization Specialist.
Analyze the following resume{' against the targeted job description' if jd_text else ''}.

--- RESUME TEXT (truncated if long) ---
{resume_text[:4500]}
"""
        if jd_text:
            prompt += f"""
--- TARGET JOB DESCRIPTION ---
{jd_text[:2500]}
"""

        prompt += """
Provide your expert evaluation in clear, formatted Markdown with these exact sections:
### 1. Executive Summary & First Impression
(A 3-sentence brutal yet constructive critique of candidate positioning, seniority level, and brand clarity)

### 2. Standout Strengths
- (Strength 1 with specific evidence)
- (Strength 2 with specific evidence)
- (Strength 3 with specific evidence)

### 3. Critical Red Flags & Missing Elements
- (Red flag 1 with fix)
- (Red flag 2 with fix)
- (Red flag 3 with fix)

### 4. High-Impact Bullet Rewrites (Google XYZ Formula)
- **Original**: (A weak/passive bullet from the resume)
  **Upgraded**: (Quantified Accomplished [X] by doing [Z] as measured by [Y])
- **Original**: (Second weak bullet)
  **Upgraded**: (Upgraded version tailored for target role)

### 5. Tailored Interview Prep Questions
- (Tough behavioral or technical question based on gaps in this resume)
- (Question probing the scale/metrics of listed achievements)
- (Role-fit situational question)
"""
        output_text, used_model = _call_gemini_with_fallback(client, prompt)

        return {
            "success": True,
            "source": f"Google Gemini ({used_model})",
            "content": output_text,
            "is_fallback": False
        }

    except Exception as e:
        error_msg = str(e)
        return _build_offline_fallback(
            resume_text,
            jd_text,
            offline_fallback_data,
            reason=f"Gemini API unavailable: {error_msg}"
        )


def generate_gemini_bullet_rewrites(
    bullet: str,
    target_role: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transforms a single bullet point into 3 distinct high-impact Google XYZ variations:
    1. Performance & Scale Focus
    2. Architecture & Leadership Focus
    3. Business Value & Cost Reduction Focus
    """
    key = get_resolved_api_key(api_key)
    if not key:
        return _build_offline_bullet_variations(bullet, target_role)

    try:
        from google import genai
        client = genai.Client(api_key=key)

        prompt = f"""
You are a senior tech career coach. Transform the following resume bullet point using Google's XYZ formula ("Accomplished [X] as measured by [Y] by doing [Z]").
Role Target: {target_role or 'Senior Technology Professional'}

Original Bullet: "{bullet}"

Generate 3 upgraded variations in Markdown:
1. **Performance & Scale Variant**: (Focus on technical metrics, throughput, latency, concurrency, user scale)
2. **Leadership & System Architecture Variant**: (Focus on technical decisions, design patterns, cross-functional leadership, mentoring)
3. **Business Value & Efficiency Variant**: (Focus on revenue impact, cost savings, time to market, KPI improvements)

Under each variant, briefly explain why it is stronger.
"""
        output_text, used_model = _call_gemini_with_fallback(client, prompt)
        return {
            "success": True,
            "source": f"Google Gemini ({used_model})",
            "content": output_text,
            "is_fallback": False
        }
    except Exception:
        return _build_offline_bullet_variations(bullet, target_role)


def _build_offline_bullet_variations(bullet: str, target_role: Optional[str] = None) -> Dict[str, Any]:
    """Generates dynamic heuristic bullet rewrites based on bullet keywords."""
    clean_b = bullet.strip().rstrip(".").strip()
    lower_b = clean_b.lower()

    # Detect theme
    if any(k in lower_b for k in ["api", "backend", "database", "server", "microservice", "query", "sql"]):
        var1 = f"Architected high-throughput services for {clean_b}, reducing p99 latency by 42% across 250K+ daily requests."
        var2 = f"Spearheaded core backend refactor for {clean_b}, establishing robust modular microservices and automated CI/CD unit testing."
        var3 = f"Streamlined infrastructure operations surrounding {clean_b}, delivering $65,000 in annual cloud compute savings."
    elif any(k in lower_b for k in ["react", "frontend", "ui", "ux", "component", "web", "css", "vue"]):
        var1 = f"Engineered modular component architecture for {clean_b}, cutting first contentful paint (FCP) time by 38% across 100K+ monthly active users."
        var2 = f"Directed cross-functional UI design system implementation for {clean_b}, standardizing reusable component libraries across 4 product squads."
        var3 = f"Revamped client-facing user workflows in {clean_b}, driving an 18% improvement in customer conversion and workflow completion rate."
    elif any(k in lower_b for k in ["model", "ml", "ai", "data", "pipeline", "train", "dataset", "deep learning"]):
        var1 = f"Developed and deployed end-to-end predictive pipelines for {clean_b}, achieving 93.4% precision and cutting inference latency by 45%."
        var2 = f"Led MLOps evaluation and containerized model rollout for {clean_b}, automating continuous retraining on multi-terabyte data streams."
        var3 = f"Quantified and productionized data intelligence workflows for {clean_b}, uncovering $180K in operational efficiencies."
    elif any(k in lower_b for k in ["cloud", "docker", "k8s", "kubernetes", "aws", "devops", "ci/cd", "terraform"]):
        var1 = f"Automated multi-region cloud deployment framework for {clean_b}, slashing deployment release cycle from 3 hours to 11 minutes."
        var2 = f"Architected infrastructure-as-code and zero-trust security policies for {clean_b}, elevating system reliability to 99.98% uptime."
        var3 = f"Consolidated distributed compute clusters for {clean_b}, cutting monthly cloud infrastructure spend by 28%."
    else:
        var1 = f"Spearheaded execution of {clean_b}, boosting team operational throughput by 35% through metric-driven milestone tracking."
        var2 = f"Designed and executed end-to-end framework for {clean_b}, collaborating cross-functionally across 3 internal stakeholder teams."
        var3 = f"Accelerated delivery timeline for {clean_b}, saving 120+ engineering hours per quarter and surpassing key SLA benchmarks."

    content = f"""
1. **Performance & Scale Variant**:
   - **Upgraded**: *{var1}*
   - **Recruiter Rationale**: Anchor the achievement with tangible numbers, throughput, or latency gains.

2. **Leadership & System Architecture Variant**:
   - **Upgraded**: *{var2}*
   - **Recruiter Rationale**: Showcases ownership, technical decisions, and strategic initiative over passive execution.

3. **Business Value & Efficiency Variant**:
   - **Upgraded**: *{var3}*
   - **Recruiter Rationale**: Translates technical tasks into direct ROI, cost reduction, and business bottom-line impact.
"""
    return {
        "success": True,
        "source": "Smart Heuristic NLP Engine (Offline Mode)",
        "content": content,
        "is_fallback": True
    }


def generate_gemini_cover_letter(
    candidate_name: str,
    resume_text: str,
    jd_text: str,
    company: str = "Hiring Team",
    job_title: str = "Target Position",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Generates an executive-tailored cover letter and recruiter LinkedIn pitch."""
    key = get_resolved_api_key(api_key)
    if not key:
        return _build_offline_cover_letter(candidate_name, resume_text, jd_text, company, job_title)

    try:
        from google import genai
        client = genai.Client(api_key=key)

        prompt = f"""
You are an executive career advisor. Craft a compelling, modern, non-cliché Cover Letter and a 150-word LinkedIn InMail outreach message.

Candidate Name: {candidate_name}
Target Company: {company}
Target Role: {job_title}

--- RESUME SUMMARY ---
{resume_text[:3500]}

--- TARGET JOB DESCRIPTION ---
{jd_text[:2000]}

Generate in clean Markdown:
### Part 1: Executive Cover Letter (300-350 words)
- Opening hook linking candidate's proven achievements with the company's technical vision
- Middle paragraph highlighting 2 quantifiable accomplishments that solve their exact requirements
- Closing with call to action

### Part 2: 150-Word LinkedIn InMail Outreach Message
- Punchy, personalized message to send directly to the hiring manager or technical recruiter
"""
        output_text, used_model = _call_gemini_with_fallback(client, prompt)
        return {
            "success": True,
            "source": f"Google Gemini ({used_model})",
            "content": output_text,
            "is_fallback": False
        }
    except Exception:
        return _build_offline_cover_letter(candidate_name, resume_text, jd_text, company, job_title)


def _build_offline_cover_letter(
    candidate_name: str,
    resume_text: str,
    jd_text: str,
    company: str,
    job_title: str
) -> Dict[str, Any]:
    """Deterministic, professional cover letter and recruiter outreach pitch."""
    content = f"""
### Part 1: Executive Cover Letter

Dear Hiring Team at {company},

I am writing to express my strong enthusiasm for the **{job_title}** position. With a proven track record of architecting scalable systems, driving high-impact technical initiatives, and translating complex product goals into performant solutions, I am eager to contribute immediately to {company}'s engineering objectives.

In reviewing your requirements, I noted your emphasis on architecting robust systems, optimizing latency and reliability, and collaborating cross-functionally. Throughout my career, I have made measurable impact a core priority:
- Spearheaded end-to-end technical implementations that increased throughput, reduced infrastructure latency by over 35%, and supported hundreds of thousands of active users.
- Collaborated across product, design, and engineering stakeholders to establish clean architectural patterns, automated CI/CD pipelines, and rigorous testing standards.

What excites me most about {company} is your commitment to technical innovation and high-velocity engineering. I look forward to bringing my deep problem-solving background, proactive ownership, and passion for engineering excellence to your team.

Thank you for your time and consideration. I welcome the opportunity to discuss how my experience aligns with your upcoming roadmap.

Sincerely,  
**{candidate_name}**

---

### Part 2: 150-Word LinkedIn Recruiter InMail Message

**Subject:** {candidate_name} — Candidate for {job_title} at {company}

Hi {company} Hiring Team,

I came across the **{job_title}** opening at {company} and was immediately drawn to your team's mission and engineering standards. 

With deep experience designing scalable architectures and driving measurable performance optimizations (including slashing service latency by over 35% and automating CI/CD workflows), I believe my background directly aligns with your current priorities.

I have attached my resume and would welcome a brief 10-minute conversation to learn more about the team's goals for this quarter.

Best regards,  
**{candidate_name}**
"""
    return {
        "success": True,
        "source": "Smart Heuristic Pitch Engine (Offline Mode)",
        "content": content,
        "is_fallback": True
    }


def _build_offline_fallback(
    resume_text: str,
    jd_text: Optional[str] = None,
    fallback_data: Optional[Dict[str, Any]] = None,
    reason: str = "Offline Mode"
) -> Dict[str, Any]:
    """Generates rich, deterministic analysis when Gemini API is unavailable."""
    data = fallback_data or {}
    metrics = data.get("metrics", {})
    verbs = data.get("verbs", {})
    matching = data.get("matching", {})
    missing_skills = matching.get("missing_skills", [])
    matching_skills = matching.get("matching_skills", [])

    weak_verbs = verbs.get("weak_phrases_used", ["worked on", "responsible for"])
    strong_verb_count = verbs.get("strong_verb_count", 0)
    metric_count = metrics.get("metric_count", 0)

    content = f"""
> [!NOTE]
> **Offline Analysis Engine Active**
> *{reason}. The report below was generated by our built-in heuristic NLP and ATS rule engine.*

### 1. Executive Summary & First Impression
Your resume demonstrates solid foundational technical competence, containing **{len(matching_skills) if matching_skills else 'multiple'} recognized industry skills**. However, your achievements could be framed with greater business impact. With **{metric_count} measurable metric(s)** detected, boosting your quantified outcomes will dramatically increase recruiter callback rates.

### 2. Standout Strengths
- **Skill Breadth**: Identified strong proficiency in key technical competencies ({', '.join(matching_skills[:5]) if matching_skills else 'core industry tools'}).
- **Action Orientation**: Deployed **{strong_verb_count}** proactive action verbs showcasing hands-on execution.
- **Section Structure**: Standard ATS-compatible section flow and readable structural density.

### 3. Critical Red Flags & Missing Elements
- **Metrics Deficit**: Only {metric_count} quantified outcome(s) found. Every bullet should ideally state *how much*, *how many*, or *percentage improved*.
- **Passive Phrasing**: Detected passive phrases ({', '.join(weak_verbs[:2]) if weak_verbs else 'responsible for'}) that soften leadership impact.
"""

    if missing_skills:
        content += f"""- **Target Job Skill Gaps**: Missing critical skills requested by the job posting: **{', '.join(missing_skills[:5])}**.
"""
    else:
        content += """- **Summary Alignment**: Ensure your professional summary clearly highlights your target job title and marquee achievement within the first 10 seconds of reading.
"""

    content += """
### 4. High-Impact Bullet Rewrites (Google XYZ Formula)
- **Original**: *Responsible for database maintenance and API bug fixes.*  
  **Upgraded**: *Refactored 14 core database query procedures and API endpoints, slashing server response latency by 32% across 200,000 monthly requests.*
- **Original**: *Worked on front-end components and added features for users.*  
  **Upgraded**: *Engineered 18+ modular, reusable UI components with responsive state management, improving conversion flow and boosting user retention by 22%.*

### 5. Tailored Interview Prep Questions
- *Walk me through a project where you solved a severe performance bottleneck. What metrics did you use to benchmark before and after?*
- *Can you describe a scenario where you had to quickly adopt a new technology or framework under a tight production deadline?*
- *How do you approach code reviews and architectural tradeoffs when balancing delivery speed against maintainability?*
"""

    return {
        "success": True,
        "source": "Local Intelligent Engine (Offline Mode)",
        "content": content,
        "is_fallback": True,
        "reason": reason
    }
