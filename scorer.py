"""
ATS Resume Scoring Engine.
Calculates multi-dimensional ATS score (0-100) with detailed component breakdowns,
weights, feedback alerts, and qualitative ratings.
"""

from typing import Dict, Any, List


def calculate_ats_score(
    analysis_data: Dict[str, Any],
    skills_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes overall ATS Score (0-100) across 5 core dimensions:
    1. Structure & Formatting (20%)
    2. Skill Breadth & Density (25%)
    3. Quantified Impact & Metrics (20%)
    4. Action Verbs & Language Strength (20%)
    5. Brevity & Section Balance (15%)
    """
    contact = analysis_data.get("contact", {})
    metrics = analysis_data.get("metrics", {})
    verbs = analysis_data.get("verbs", {})
    structure = analysis_data.get("structure", {})
    flat_skills = skills_data.get("flat_skills", [])
    category_dist = skills_data.get("category_distribution", {})

    breakdown = {}
    feedback_notes: List[Dict[str, str]] = []

    # 1. Structure & Formatting (20%)
    struct_score = 0
    if contact.get("email"):
        struct_score += 25
    else:
        feedback_notes.append({"type": "critical", "msg": "Missing email address in contact section."})

    if contact.get("phone"):
        struct_score += 20
    else:
        feedback_notes.append({"type": "warning", "msg": "Missing phone number in contact section."})

    if contact.get("linkedin"):
        struct_score += 15
    else:
        feedback_notes.append({"type": "tip", "msg": "Add your LinkedIn profile link to improve recruiter discovery."})

    # Core sections check
    missing_required = structure.get("missing_required_sections", [])
    if not missing_required:
        struct_score += 25
    else:
        penalty = len(missing_required) * 10
        struct_score += max(0, 25 - penalty)
        feedback_notes.append({"type": "critical", "msg": f"Missing critical section(s): {', '.join(missing_required)}."})

    # Length score
    length_score_contribution = structure.get("length_score", 70) * 0.15
    struct_score += length_score_contribution
    struct_score = min(100, int(struct_score))
    breakdown["Structure & Formatting"] = {
        "score": struct_score,
        "weight": 0.20,
        "description": "Contact info, key headings, and ATS-parseable layout."
    }

    # 2. Skill Breadth & Density (25%)
    # Target: 10-25 distinct industry skills, spanning at least 3 categories
    skill_count = len(flat_skills)
    cat_count = len(category_dist)

    skill_score = 0
    if skill_count >= 18:
        skill_score += 60
    elif skill_count >= 10:
        skill_score += 45
    elif skill_count >= 5:
        skill_score += 30
    else:
        skill_score += 15
        feedback_notes.append({"type": "warning", "msg": "Low skill keyword density. Add technical and domain proficiencies."})

    # Category diversity
    if cat_count >= 4:
        skill_score += 40
    elif cat_count >= 2:
        skill_score += 25
    else:
        skill_score += 10
        feedback_notes.append({"type": "tip", "msg": "Diversify skills across languages, frameworks, cloud, and tools."})

    skill_score = min(100, int(skill_score))
    breakdown["Skill Density & Breadth"] = {
        "score": skill_score,
        "weight": 0.25,
        "description": "Recognized technical proficiencies, frameworks, and tools."
    }

    # 3. Quantified Impact & Metrics (20%)
    # Target: At least 4-8 quantifiable metrics (%, $, numbers) proving impact
    metric_count = metrics.get("metric_count", 0)
    bullet_count = metrics.get("impact_bullet_count", 0)

    metric_score = 0
    if metric_count >= 7:
        metric_score = 100
    elif metric_count >= 4:
        metric_score = 80
    elif metric_count >= 2:
        metric_score = 55
        feedback_notes.append({"type": "tip", "msg": "Include more numbers, percentages, and scale metrics in your bullet points."})
    elif metric_count == 1:
        metric_score = 35
        feedback_notes.append({"type": "warning", "msg": "Only 1 quantifiable metric found. Recruiters favor results with numbers."})
    else:
        metric_score = 20
        feedback_notes.append({"type": "critical", "msg": "Zero quantifiable achievements found! Quantify results (e.g., 'reduced latency by 35%')."})

    breakdown["Quantified Impact & Results"] = {
        "score": metric_score,
        "weight": 0.20,
        "description": "Numbers, percentages, revenue, and scale proving business value."
    }

    # 4. Action Verbs & Language Strength (20%)
    strong_verbs = verbs.get("strong_verb_count", 0)
    weak_phrases = verbs.get("weak_phrases_count", 0)

    verb_score = 0
    if strong_verbs >= 12:
        verb_score += 70
    elif strong_verbs >= 7:
        verb_score += 50
    elif strong_verbs >= 3:
        verb_score += 30
    else:
        verb_score += 15
        feedback_notes.append({"type": "warning", "msg": "Few strong action verbs detected. Start bullets with words like 'Architected', 'Spearheaded', 'Optimized'."})

    # Penalty for passive clichés
    passive_penalty = min(30, weak_phrases * 10)
    if weak_phrases == 0:
        verb_score += 30
    else:
        verb_score += max(0, 30 - passive_penalty)
        feedback_notes.append({"type": "warning", "msg": f"Detected {weak_phrases} passive phrase(s) like 'responsible for' or 'worked on'. Replace with decisive action verbs."})

    verb_score = min(100, int(verb_score))
    breakdown["Action Verbs & Impact Tone"] = {
        "score": verb_score,
        "weight": 0.20,
        "description": "Proactive action verbs over passive clichés."
    }

    # 5. Brevity & Readability (15%)
    brevity_score = structure.get("length_score", 75)
    word_count = structure.get("word_count", 0)

    if word_count < 200:
        feedback_notes.append({"type": "critical", "msg": "Resume is too short. Include more detail on projects and experience."})
    elif word_count > 1500:
        feedback_notes.append({"type": "tip", "msg": "Resume is unusually long. Try streamlining to 1-2 focused pages."})

    brevity_score = min(100, int(brevity_score))
    breakdown["Brevity & Balance"] = {
        "score": brevity_score,
        "weight": 0.15,
        "description": "Optimal word count, readable pacing, and layout density."
    }

    # Overall calculation
    total_ats_score = sum(item["score"] * item["weight"] for item in breakdown.values())
    total_ats_score = round(total_ats_score, 1)

    # Grade & verdict
    if total_ats_score >= 85:
        grade = "A+"
        verdict = "Excellent ATS Match (Top Tier)"
        status_color = "#10b981"
    elif total_ats_score >= 72:
        grade = "A"
        verdict = "Strong ATS Candidate (Interview Ready)"
        status_color = "#3b82f6"
    elif total_ats_score >= 55:
        grade = "B"
        verdict = "Moderate ATS Score (Needs Optimization)"
        status_color = "#f59e0b"
    else:
        grade = "C"
        verdict = "Low ATS Score (High Risk of Rejection)"
        status_color = "#ef4444"

    return {
        "total_ats_score": total_ats_score,
        "grade": grade,
        "verdict": verdict,
        "status_color": status_color,
        "breakdown": breakdown,
        "feedback_notes": feedback_notes
    }
