"""
Resume Content & Structure Analyzer.
Extracts contact information, detects education degrees, analyzes work experience,
evaluates quantifiable impact metrics, and calculates structural health signals.
"""

import re
from typing import Dict, List, Any, Tuple


# Action verbs dictionary
STRONG_ACTION_VERBS = [
    "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered",
    "advised", "advocated", "amplified", "analyzed", "architected", "automated",
    "boosted", "budgeted", "built", "centralized", "championed", "coached",
    "collaborated", "compiled", "composed", "conceived", "configured", "consolidated",
    "constructed", "coordinated", "created", "customized", "debugged", "decreased",
    "defined", "delivered", "deployed", "designed", "developed", "devised",
    "diagnosed", "directed", "documented", "doubled", "drove", "eliminated",
    "engineered", "enhanced", "established", "evaluated", "exceeded", "executed",
    "expanded", "expedited", "fabricated", "facilitated", "forecasted", "formulated",
    "fostered", "founded", "generated", "guided", "halted", "headed", "identified",
    "implemented", "improved", "increased", "initiated", "innovated", "inspected",
    "installed", "instituted", "instructed", "integrated", "intensified", "introduced",
    "invented", "investigated", "launched", "led", "leveraged", "managed",
    "maximized", "mentored", "migrated", "minimized", "modernized", "monitored",
    "negotiated", "optimized", "orchestrated", "organized", "originated", "overhauled",
    "oversaw", "partnered", "pioneered", "planned", "produced", "programmed",
    "promoted", "published", "rebuilt", "redesigned", "reduced", "reengineered",
    "refactored", "refined", "remodeled", "reorganized", "replaced", "resolved",
    "restructured", "revamped", "reviewed", "revitalized", "safeguarded", "scaled",
    "scheduled", "secured", "simplified", "slashed", "spearheaded", "standardized",
    "streamlined", "strengthened", "structured", "supervised", "surpassed", "trained",
    "transformed", "transitioned", "tripled", "troubleshot", "unified", "upgraded"
]

WEAK_PASSIVE_PHRASES = [
    "responsible for", "duties included", "worked on", "helped with", "assisted in",
    "tasked with", "handled", "was involved in", "participated in", "served as",
    "attempted to", "tried to", "daily duties"
]

DEGREE_PATTERNS = [
    r"\b(Ph\.?D\.?|Doctor of Philosophy)\b",
    r"\b(Master'?s|M\.?S\.?|M\.?Sc\.?|M\.?Tech|MBA|M\.?Eng|M\.?A\.?)\b",
    r"\b(Bachelor'?s|B\.?S\.?|B\.?Sc\.?|B\.?Tech|B\.?E\.?|B\.?A\.?|BBA)\b",
    r"\b(Associate'?s|A\.?S\.?|A\.?A\.?)\b",
    r"\b(Diploma|Post Graduate|Nanodegree|Bootcamp)\b"
]


def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract email, phone, links (LinkedIn, GitHub, Portfolio) from text."""
    # Email
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = re.findall(email_regex, text)
    email = emails[0] if emails else None

    # Phone (US & International formats)
    phone_regex = r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}(?:[-.\s]?\d{1,4})?)"
    phones = [p.strip() for p in re.findall(phone_regex, text) if len(re.sub(r"\D", "", p)) >= 10 and len(re.sub(r"\D", "", p)) <= 14]
    phone = phones[0] if phones else None

    # LinkedIn
    linkedin_regex = r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/[a-zA-Z0-9_-]+"
    linkedin_matches = re.findall(linkedin_regex, text, re.IGNORECASE)
    linkedin = linkedin_matches[0] if linkedin_matches else None

    # GitHub
    github_regex = r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+"
    github_matches = re.findall(github_regex, text, re.IGNORECASE)
    github = github_matches[0] if github_matches else None

    # General Portfolio / Website (excluding common domains like linkedin, github, gmail)
    url_regex = r"https?:\/\/(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?"
    all_urls = re.findall(url_regex, text)
    portfolio = None
    for url in all_urls:
        if not re.search(r"linkedin|github|twitter|x\.com|facebook|instagram", url, re.IGNORECASE):
            portfolio = url
            break

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "has_complete_contact": bool(email and phone)
    }


def extract_education(text: str) -> List[str]:
    """Detect degree types mentioned in resume text."""
    found_degrees = []
    for pattern in DEGREE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            clean = m.strip().replace(".", "")
            if clean not in found_degrees:
                found_degrees.append(clean)
    return found_degrees


def extract_quantifiable_metrics(text: str) -> Dict[str, Any]:
    """
    Identify metrics (percentages, dollar amounts, multiples, numbers showing scale)
    which prove tangible impact on an ATS resume.
    """
    # Bullet points / lines extraction
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    metric_regex = r"(?:\d+(?:\.\d+)?%|\$\s?\d+(?:,\d+)*(?:\.\d+)?(?:\s?[kKmMbB]|million|billion)?|\b\d+x\b|\b\d+\s?(?:users|clients|engineers|microservices|req\/s|rps|queries|requests|seconds|minutes|hours|days|weeks|months|years|ms)\b)"
    
    impact_bullets = []
    all_found_metrics = []

    for line in lines:
        matches = re.findall(metric_regex, line, re.IGNORECASE)
        if matches:
            all_found_metrics.extend(matches)
            if len(line) > 25:
                impact_bullets.append(line)

    unique_metrics = list(dict.fromkeys(all_found_metrics))

    return {
        "metric_count": len(all_found_metrics),
        "unique_metrics": unique_metrics[:15],
        "impact_bullet_count": len(impact_bullets),
        "sample_impact_bullets": impact_bullets[:5]
    }


def analyze_action_verbs(text: str) -> Dict[str, Any]:
    """Analyze the usage of high-impact action verbs vs passive phrases."""
    text_lower = text.lower()
    
    found_strong = []
    for verb in STRONG_ACTION_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            found_strong.append(verb.capitalize())

    found_weak = []
    for phrase in WEAK_PASSIVE_PHRASES:
        if phrase in text_lower:
            found_weak.append(phrase)

    return {
        "strong_verb_count": len(found_strong),
        "strong_verbs_used": sorted(found_strong),
        "weak_phrases_count": len(found_weak),
        "weak_phrases_used": found_weak
    }


def analyze_resume_structure(text: str, sections: Dict[str, str], num_pages: int = 1) -> Dict[str, Any]:
    """
    Audit document length, word density, reading time, and structural completeness.
    """
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    estimated_read_time_min = round(word_count / 200, 1) if word_count > 0 else 0

    # Section presence checks
    required_sections = ["experience", "education", "skills"]
    recommended_sections = ["summary", "projects", "certifications"]

    missing_required = [sec for sec in required_sections if sec not in sections or len(sections[sec]) < 30]
    present_recommended = [sec for sec in recommended_sections if sec in sections and len(sections[sec]) >= 30]

    # Length status
    if word_count < 200:
        length_status = "Too Short (under 200 words, ATS may rank low)"
        length_score = 40
    elif 300 <= word_count <= 850:
        length_status = "Optimal Single Page Length"
        length_score = 100
    elif 851 <= word_count <= 1400:
        length_status = "Optimal 2-Page Length"
        length_score = 95
    else:
        length_status = "Potentially Verbose (over 1400 words)"
        length_score = 70

    return {
        "word_count": word_count,
        "read_time_minutes": estimated_read_time_min,
        "num_pages": num_pages,
        "length_status": length_status,
        "length_score": length_score,
        "missing_required_sections": missing_required,
        "present_recommended_sections": present_recommended,
        "total_sections_found": len(sections)
    }


def analyze_full_resume(text: str, sections: Dict[str, str], num_pages: int = 1) -> Dict[str, Any]:
    """Consolidated master analysis for a parsed resume."""
    contact = extract_contact_info(text)
    education = extract_education(text)
    metrics = extract_quantifiable_metrics(text)
    verbs = analyze_action_verbs(text)
    structure = analyze_resume_structure(text, sections, num_pages)

    return {
        "contact": contact,
        "education": education,
        "metrics": metrics,
        "verbs": verbs,
        "structure": structure
    }
