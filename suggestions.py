"""
Personalized Resume Suggestions & Bullet Enhancer Engine.
Implements Google XYZ formula recommendations, action verb upgrades,
and section-specific actionable feedback.
"""

from typing import Dict, List, Any, Optional
from modules.gemini_client import generate_gemini_bullet_rewrites

__all__ = [
    "ACTION_VERB_REPLACEMENTS",
    "XYZ_TEMPLATES",
    "generate_tailored_suggestions",
    "transform_bullet_point",
]

ACTION_VERB_REPLACEMENTS: Dict[str, List[str]] = {
    "worked on": ["Architected", "Engineered", "Developed", "Spearheaded", "Implemented"],
    "responsible for": ["Led", "Directed", "Executed", "Oversaw", "Managed"],
    "helped with": ["Collaborated to", "Partnered with", "Facilitated", "Accelerated"],
    "assisted in": ["Contributed to", "Co-engineered", "Supported execution of"],
    "handled": ["Orchestrated", "Administered", "Streamlined", "Resolved"],
    "did": ["Executed", "Delivered", "Completed", "Produced"],
    "tasked with": ["Spearheaded", "Undertook", "Drove the initiative to"]
}

XYZ_TEMPLATES: List[Dict[str, str]] = [
    {
        "role": "Software Engineering & Backend",
        "before": "Worked on backend APIs and made database queries faster.",
        "after": "Architected 12+ RESTful microservices using FastAPI and PostgreSQL, reducing query latency by 42% and supporting 15,000+ daily active users."
    },
    {
        "role": "Frontend & Web Development",
        "before": "Built UI components in React and fixed bugs.",
        "after": "Engineered responsive dashboard interfaces using React, TypeScript, and Tailwind CSS, increasing page load speed by 35% and boosting user retention by 18%."
    },
    {
        "role": "AI / Data Science & ML",
        "before": "Built machine learning models for customer churn.",
        "after": "Developed and deployed an end-to-end XGBoost and PyTorch churn prediction pipeline, saving $240K annually by identifying at-risk accounts with 91% precision."
    },
    {
        "role": "Cloud, DevOps & Infrastructure",
        "before": "Set up CI/CD pipelines and managed AWS servers.",
        "after": "Spearheaded automated CI/CD migration using GitHub Actions and Terraform on AWS EKS, slashing deployment cycle times from 4 hours to 12 minutes."
    }
]


def generate_tailored_suggestions(
    analysis_data: Dict[str, Any],
    skills_data: Dict[str, Any],
    match_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates tailored, prioritized improvement recommendations.
    Categorized into:
    - High Priority Fixes (Critical ATS blockers)
    - Medium Priority Polishes (Competitiveness boosters)
    - Action Verb Upgrades
    - XYZ Formula Examples
    - Keyword Insertion Blueprint (if JD is provided)
    """
    contact = analysis_data.get("contact", {})
    metrics = analysis_data.get("metrics", {})
    verbs = analysis_data.get("verbs", {})
    structure = analysis_data.get("structure", {})
    missing_required = structure.get("missing_required_sections", [])

    high_priority = []
    medium_priority = []
    tips_by_section = {}

    # 1. Contact Info Audit
    if not contact.get("email"):
        high_priority.append("Add a professional email address at the very top of your resume.")
    if not contact.get("phone"):
        high_priority.append("Add a valid phone number with country/area code.")
    if not contact.get("linkedin"):
        medium_priority.append("Include your clickable LinkedIn profile URL.")
    if not contact.get("github") and "Programming Languages" in skills_data.get("found_by_category", {}):
        medium_priority.append("Add your GitHub profile link showcasing your open-source code and projects.")

    # 2. Critical Section Audit
    if missing_required:
        high_priority.append(f"Add missing core section headings: {', '.join([s.title() for s in missing_required])}.")

    # 3. Quantifiable Impact Audit
    metric_count = metrics.get("metric_count", 0)
    if metric_count < 3:
        high_priority.append(
            f"Quantify your accomplishments! Only {metric_count} metric(s) found. "
            "Use the Google XYZ Formula: 'Accomplished [X] as measured by [Y] by doing [Z]' with numbers (%, $, time saved, user growth)."
        )
    elif metric_count < 6:
        medium_priority.append(
            "Strengthen existing bullets with concrete numbers: latency reduction %, revenue impact, team size led, or requests handled per second."
        )

    # 4. Action Verbs Audit
    weak_count = verbs.get("weak_phrases_count", 0)
    if weak_count > 0:
        high_priority.append(
            f"Replace {weak_count} weak passive phrase(s) (e.g., 'responsible for', 'worked on') with powerful action verbs like 'Architected', 'Spearheaded', 'Optimized'."
        )

    # 5. Section-specific guidance
    tips_by_section["Professional Summary"] = [
        "Keep it concise (3-4 sentences max).",
        "Lead with your primary title, total years of experience, and top 3 core technical specializations.",
        "Highlight your single biggest career achievement with an impressive quantitative metric."
    ]

    tips_by_section["Work Experience"] = [
        "Format every bullet point: [Strong Action Verb] + [Task / Project Scope] + [Quantified Business Impact].",
        "Keep each bullet point between 1.5 to 2.5 lines; avoid monolithic walls of text.",
        "Place your most impressive, metric-driven achievements in the top 2 bullets for each role."
    ]

    tips_by_section["Skills Section"] = [
        "Organize skills into logical sub-categories (Languages, Frameworks, Cloud, Databases, Tools) rather than one unstructured block.",
        "List skills in order of true proficiency and relevance to your target job.",
        "Remove outdated or obsolete technologies (e.g. Flash, jQuery 1.x) unless specifically required."
    ]

    tips_by_section["Projects"] = [
        "Include live demo links and GitHub repository links for every listed project.",
        "Explicitly mention the full tech stack used in the project header (e.g. 'Tech: React, FastAPI, Docker, AWS').",
        "State the problem, your solution, and user adoption or benchmark performance numbers."
    ]

    # 6. Target Job Description Keyword Strategy
    keyword_strategy = []
    if match_data and match_data.get("missing_skills"):
        missing = match_data.get("missing_skills", [])
        for skill in missing[:6]:
            keyword_strategy.append({
                "skill": skill,
                "recommendation": f"Add '{skill}' to your Skills section and incorporate it into at least 1 recent project or experience bullet point where you applied it."
            })

    return {
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "tips_by_section": tips_by_section,
        "keyword_strategy": keyword_strategy,
        "action_verb_replacements": ACTION_VERB_REPLACEMENTS,
        "xyz_templates": XYZ_TEMPLATES
    }


def transform_bullet_point(
    bullet: str,
    target_role: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transforms any candidate bullet into 3 Google XYZ variants
    using either live Gemini or the built-in heuristic NLP engine.
    """
    return generate_gemini_bullet_rewrites(
        bullet=bullet,
        target_role=target_role,
        api_key=api_key
    )
