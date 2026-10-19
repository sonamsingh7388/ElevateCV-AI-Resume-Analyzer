"""
Multi-Candidate Resume Comparator & Benchmarking Module.
Allows recruiters or job seekers to compare multiple candidate profiles or resume versions
side-by-side against a target job description.
"""

from typing import List, Dict, Any
import pandas as pd

from modules.parser import segment_sections
from modules.skills_bank import extract_skills
from modules.analyzer import analyze_full_resume
from modules.scorer import calculate_ats_score
from modules.matcher import compare_resume_to_job


def compare_candidates(
    candidates: List[Dict[str, str]],
    jd_text: str
) -> Dict[str, Any]:
    """
    Evaluates multiple candidates against a single job description.
    candidates: list of {"name": str, "resume_text": str}
    """
    if not candidates or not jd_text.strip():
        return {
            "summary_table": [],
            "candidates_details": [],
            "best_match_candidate": None,
            "best_ats_candidate": None
        }

    details = []
    summary_rows = []

    for cand in candidates:
        name = cand.get("name", "Candidate")
        text = cand.get("resume_text", "")
        if not text.strip():
            continue

        sections = segment_sections(text)
        skills = extract_skills(text)
        analysis = analyze_full_resume(text, sections)
        ats = calculate_ats_score(analysis, skills)
        match = compare_resume_to_job(text, jd_text)

        cand_info = {
            "name": name,
            "ats_score": ats["total_ats_score"],
            "grade": ats["grade"],
            "verdict": ats["verdict"],
            "match_score": match["match_score"],
            "matching_skills_count": len(match["matching_skills"]),
            "missing_skills_count": len(match["missing_skills"]),
            "total_skills_count": len(skills["flat_skills"]),
            "metrics_count": analysis["metrics"]["metric_count"],
            "word_count": analysis["structure"]["word_count"],
            "breakdown": ats["breakdown"],
            "matching_skills": match["matching_skills"],
            "missing_skills": match["missing_skills"]
        }
        details.append(cand_info)

        summary_rows.append({
            "Candidate": name,
            "ATS Score": f"{ats['total_ats_score']}/100 ({ats['grade']})",
            "Job Match %": f"{match['match_score']}%",
            "Matching Skills": len(match["matching_skills"]),
            "Missing Skills": len(match["missing_skills"]),
            "Impact Metrics": analysis["metrics"]["metric_count"],
            "Total Skills": len(skills["flat_skills"]),
            "Verdict": ats["verdict"]
        })

    # Find leaders
    best_match = max(details, key=lambda x: x["match_score"]) if details else None
    best_ats = max(details, key=lambda x: x["ats_score"]) if details else None

    return {
        "summary_table": summary_rows,
        "candidates_details": details,
        "best_match_candidate": best_match["name"] if best_match else None,
        "best_ats_candidate": best_ats["name"] if best_ats else None
    }
