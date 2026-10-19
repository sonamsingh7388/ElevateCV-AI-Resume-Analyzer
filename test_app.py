"""
End-to-End Test Suite for ElevateCV Resume Analyzer.
Verifies parser, analyzer, skills bank, scorer, matcher, suggestions, charts, and Gemini client.
"""

import os
import unittest
from modules.parser import extract_text, segment_sections, ResumeParseError
from modules.skills_bank import extract_skills, SKILL_CATEGORIES
from modules.analyzer import analyze_full_resume, extract_contact_info, extract_quantifiable_metrics
from modules.scorer import calculate_ats_score
from modules.matcher import compare_resume_to_job, PRESET_JOB_DESCRIPTIONS, compute_tf_idf_similarity
from modules.suggestions import generate_tailored_suggestions
from modules.gemini_client import generate_gemini_critique, is_gemini_available
from modules.charts import create_gauge_chart, create_radar_chart, create_category_bar_chart


class TestElevateCV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.docx_sample = os.path.join("sample_resumes", "sample_software_engineer.docx")
        cls.pdf_sample = os.path.join("sample_resumes", "sample_data_scientist.pdf")

    def test_docx_parser(self):
        self.assertTrue(os.path.exists(self.docx_sample), "Sample DOCX should exist.")
        with open(self.docx_sample, "rb") as f:
            res = extract_text(f.read(), "sample_software_engineer.docx")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "DOCX")
        self.assertIn("alex rivera", res["text"].lower())
        self.assertGreater(len(res["text"]), 500)

    def test_pdf_parser(self):
        self.assertTrue(os.path.exists(self.pdf_sample), "Sample PDF should exist.")
        with open(self.pdf_sample, "rb") as f:
            res = extract_text(f.read(), "sample_data_scientist.pdf")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "PDF")
        self.assertIn("priya sharma", res["text"].lower())
        self.assertEqual(res["num_pages"], 1)

    def test_empty_or_corrupt_parser_handling(self):
        res = extract_text(b"corrupt binary data", "corrupt.pdf")
        self.assertFalse(res["success"])
        self.assertIsNotNone(res["error"])

    def test_skills_bank_categories(self):
        self.assertGreaterEqual(len(SKILL_CATEGORIES), 8)
        sample_text = "Experienced in Python, React, AWS, Docker, PyTorch, PostgreSQL, and Git."
        extracted = extract_skills(sample_text)
        found = extracted["flat_skills"]
        self.assertIn("Python", found)
        self.assertIn("React", found)
        self.assertIn("AWS", found)
        self.assertIn("Docker", found)
        self.assertIn("PyTorch", found)
        self.assertIn("PostgreSQL", found)
        self.assertIn("Git", found)

    def test_analyzer_contact_and_metrics(self):
        text = """
        John Doe
        john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe
        Spearheaded migration reducing costs by 35% and saving $150K across 10,000 users.
        """
        contact = extract_contact_info(text)
        self.assertEqual(contact["email"], "john.doe@example.com")
        self.assertEqual(contact["phone"], "(555) 123-4567")
        self.assertIn("johndoe", contact["linkedin"])
        self.assertIn("johndoe", contact["github"])

        metrics = extract_quantifiable_metrics(text)
        self.assertGreaterEqual(metrics["metric_count"], 2)

    def test_ats_scorer(self):
        with open(self.docx_sample, "rb") as f:
            res = extract_text(f.read(), "sample_software_engineer.docx")
        sections = segment_sections(res["text"])
        skills = extract_skills(res["text"])
        analysis = analyze_full_resume(res["text"], sections)
        score_data = calculate_ats_score(analysis, skills)

        self.assertGreater(score_data["total_ats_score"], 70)
        self.assertIn("Structure & Formatting", score_data["breakdown"])
        self.assertIn("Skill Density & Breadth", score_data["breakdown"])

    def test_job_matcher(self):
        with open(self.docx_sample, "rb") as f:
            res = extract_text(f.read(), "sample_software_engineer.docx")
        jd = PRESET_JOB_DESCRIPTIONS["Senior Full-Stack AI Engineer"]
        match = compare_resume_to_job(res["text"], jd)

        self.assertGreater(match["match_score"], 20.0)
        self.assertGreater(len(match["matching_skills"]), 5)
        self.assertIn("Python", match["matching_skills"])

    def test_gemini_offline_fallback(self):
        critique = generate_gemini_critique(
            resume_text="Senior Developer with 5 years experience.",
            api_key=""
        )
        self.assertTrue(critique["success"])
        self.assertTrue(critique["is_fallback"])
        self.assertIn("Offline", critique["source"])
        self.assertIn("Executive Summary", critique["content"])

    def test_charts_generation(self):
        gauge = create_gauge_chart(85.0, "Test Gauge")
        self.assertIsNotNone(gauge)

        radar = create_radar_chart({
            "Structure": {"score": 90},
            "Skills": {"score": 80},
            "Impact": {"score": 70},
            "Verbs": {"score": 85},
            "Brevity": {"score": 95}
        })
        self.assertIsNotNone(radar)

        bar = create_category_bar_chart({"Frontend": 5, "Backend": 8, "Cloud": 6})
        self.assertIsNotNone(bar)

    def test_dynamic_bullet_rewrites(self):
        from modules.suggestions import transform_bullet_point
        res = transform_bullet_point("Worked on backend database queries and helped with APIs.")
        self.assertTrue(res["success"])
        self.assertIn("Variant", res["content"])

    def test_resume_optimization_and_docx_export(self):
        from modules.resume_generator import optimize_sections, export_resume_to_docx
        sections = {
            "summary": "Experienced engineer with a passion for building software.",
            "skills": "Python, JavaScript, Docker",
            "experience": "- Responsible for database queries and worked on backend APIs."
        }
        optimized = optimize_sections(sections, missing_skills=["Kubernetes", "AWS"], weak_verbs=["worked on"])
        self.assertIn("Kubernetes", optimized["skills"])
        self.assertNotIn("responsible for", optimized["experience"].lower())

        docx_bytes = export_resume_to_docx(
            candidate_name="Jane Doe",
            contact_info={"email": "jane@example.com", "phone": "123-456-7890"},
            sections_dict=optimized
        )
        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 1000)

    def test_cover_letter_and_pitch(self):
        from modules.cover_letter import generate_cover_letter_and_pitch, export_cover_letter_to_docx
        res = generate_cover_letter_and_pitch(
            candidate_name="Alex Rivera",
            resume_text="Senior Full-Stack Engineer with 5 years experience in Python and React.",
            jd_text="Looking for a Full-Stack Engineer to build web applications.",
            company="Acme Corp",
            job_title="Senior Engineer"
        )
        self.assertTrue(res["success"])
        self.assertIn("Acme Corp", res["content"])
        self.assertIn("Alex Rivera", res["content"])

        docx_bytes = export_cover_letter_to_docx(
            candidate_name="Alex Rivera",
            contact_info={"email": "alex@example.com"},
            company="Acme Corp",
            job_title="Senior Engineer",
            letter_text=res["content"]
        )
        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 1000)

    def test_comparator(self):
        from modules.comparator import compare_candidates
        from modules.charts import create_candidate_comparison_chart
        candidates = [
            {"name": "Alex Rivera", "resume_text": "Experienced Python, React, Docker developer."},
            {"name": "Priya Sharma", "resume_text": "Data scientist with PyTorch, Machine Learning, Python."}
        ]
        jd = "Requirements: Python, React, Machine Learning, Docker"
        res = compare_candidates(candidates, jd)
        self.assertEqual(len(res["summary_table"]), 2)
        self.assertIsNotNone(res["best_match_candidate"])

        chart = create_candidate_comparison_chart(res["candidates_details"])
        self.assertIsNotNone(chart)


if __name__ == "__main__":
    unittest.main()

