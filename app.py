"""
ElevateCV — Advanced AI Resume Analyzer & ATS Optimization Engine.
An enterprise-grade, comprehensive Streamlit web application.
"""

import os
import io
import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any

# Internal modules
from modules.parser import extract_text, segment_sections
from modules.skills_bank import extract_skills
from modules.analyzer import analyze_full_resume
from modules.scorer import calculate_ats_score
from modules.matcher import compare_resume_to_job, PRESET_JOB_DESCRIPTIONS
from modules.suggestions import generate_tailored_suggestions, transform_bullet_point, ACTION_VERB_REPLACEMENTS
from modules.gemini_client import generate_gemini_critique, is_gemini_available
from modules.charts import (
    create_gauge_chart,
    create_radar_chart,
    create_category_bar_chart,
    create_candidate_comparison_chart,
    create_multi_radar_comparison_chart
)
from modules.resume_generator import (
    optimize_sections,
    export_resume_to_docx,
    generate_full_resume_markdown
)
from modules.cover_letter import (
    generate_cover_letter_and_pitch,
    export_cover_letter_to_docx
)
from modules.comparator import compare_candidates


# Page configuration
st.set_page_config(
    page_title="ElevateCV — AI Resume Analyzer & ATS Optimizer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session states
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""
if "resume_file_name" not in st.session_state:
    st.session_state["resume_file_name"] = ""
if "num_pages" not in st.session_state:
    st.session_state["num_pages"] = 1
if "target_jd" not in st.session_state:
    st.session_state["target_jd"] = PRESET_JOB_DESCRIPTIONS["Senior Full-Stack AI Engineer"]
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")
if "optimized_sections" not in st.session_state:
    st.session_state["optimized_sections"] = None
if "simulated_added_skills" not in st.session_state:
    st.session_state["simulated_added_skills"] = []


# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("## 🎯 ElevateCV")
    st.markdown("<p style='color:#94a3b8; font-size:0.85rem; margin-top:-10px;'>Enterprise AI Resume & ATS Intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 📄 1. Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload PDF, DOCX, or TXT file",
        type=["pdf", "docx", "txt"],
        help="Upload your latest resume in PDF, Word (DOCX), or plain text format."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        parsed = extract_text(file_bytes, uploaded_file.name)
        if parsed["success"]:
            st.session_state["resume_text"] = parsed["text"]
            st.session_state["resume_file_name"] = uploaded_file.name
            st.session_state["num_pages"] = parsed.get("num_pages", 1)
            st.session_state["optimized_sections"] = None
            st.success(f"✓ Loaded: {uploaded_file.name}")
        else:
            st.error(f"Error parsing file: {parsed['error']}")

    st.markdown("<p style='font-size:0.8rem; color:#94a3b8; margin-top:8px;'>Or load a test candidate profile:</p>", unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("👨‍💻 Full Stack (.docx)", use_container_width=True):
            sample_docx_path = os.path.join("sample_resumes", "sample_software_engineer.docx")
            if os.path.exists(sample_docx_path):
                with open(sample_docx_path, "rb") as f:
                    res = extract_text(f.read(), "sample_software_engineer.docx")
                    st.session_state["resume_text"] = res["text"]
                    st.session_state["resume_file_name"] = "Alex_Rivera_Senior_FullStack.docx"
                    st.session_state["num_pages"] = 1
                    st.session_state["target_jd"] = PRESET_JOB_DESCRIPTIONS["Senior Full-Stack AI Engineer"]
                    st.session_state["optimized_sections"] = None
                    st.rerun()

    with col_s2:
        if st.button("🔬 Data Scientist (.pdf)", use_container_width=True):
            sample_pdf_path = os.path.join("sample_resumes", "sample_data_scientist.pdf")
            if os.path.exists(sample_pdf_path):
                with open(sample_pdf_path, "rb") as f:
                    res = extract_text(f.read(), "sample_data_scientist.pdf")
                    st.session_state["resume_text"] = res["text"]
                    st.session_state["resume_file_name"] = "Dr_Priya_Sharma_DataScientist.pdf"
                    st.session_state["num_pages"] = 1
                    st.session_state["target_jd"] = PRESET_JOB_DESCRIPTIONS["Senior Data Scientist / ML Engineer"]
                    st.session_state["optimized_sections"] = None
                    st.rerun()

    st.markdown("---")
    st.markdown("### 💼 2. Target Job Description")
    preset_choice = st.selectbox(
        "Choose Preset Role or Custom:",
        options=list(PRESET_JOB_DESCRIPTIONS.keys()) + ["Custom Job Description"],
        index=0
    )

    if preset_choice != "Custom Job Description":
        st.session_state["target_jd"] = PRESET_JOB_DESCRIPTIONS[preset_choice]

    target_jd_input = st.text_area(
        "Job Description Text:",
        value=st.session_state["target_jd"],
        height=130,
        help="Paste the target job description to run keyword match & gap analysis."
    )
    st.session_state["target_jd"] = target_jd_input

    st.markdown("---")
    st.markdown("### 🤖 3. AI Engine Configuration")
    user_api_key = st.text_input(
        "Google Gemini API Key (Optional):",
        value=st.session_state["gemini_api_key"],
        type="password",
        help="Enter your Gemini API key to activate Gemini live deep critique. If omitted, the app runs on full offline heuristic intelligence."
    )
    st.session_state["gemini_api_key"] = user_api_key

    if is_gemini_available(user_api_key):
        st.markdown("<span style='color:#10b981; font-size:0.85rem; font-weight:600;'>🟢 Gemini Active</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#f59e0b; font-size:0.85rem; font-weight:600;'>🟡 Built-in Heuristic Engine (Offline Active)</span>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.75rem; color:#64748b; margin-top:4px;'>🔐 API keys are kept strictly in memory and never persisted or shared.</p>", unsafe_allow_html=True)

    if st.session_state["resume_text"]:
        st.markdown("---")
        if st.button("🔄 Reset / Clear Session", use_container_width=True):
            st.session_state["resume_text"] = ""
            st.session_state["resume_file_name"] = ""
            st.session_state["optimized_sections"] = None
            st.session_state["simulated_added_skills"] = []
            st.rerun()


# --- MAIN CONTENT AREA ---
st.markdown("<div class='hero-title'>🎯 ElevateCV — AI Resume Analyzer & ATS Optimizer</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Enterprise-grade ATS resume scoring, multi-category skill extraction, Google XYZ formula rewriter, live resume studio, and custom cover letter generation.</div>", unsafe_allow_html=True)

resume_text = st.session_state.get("resume_text", "").strip()

if not resume_text:
    # Empty State: Showcase features & instructions
    st.info("👋 Welcome! Please upload your resume in the left sidebar or click one of the sample candidate buttons to begin instant analysis.")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        st.markdown("""
        <div class='glass-card'>
            <h4>🎯 ATS Scoring</h4>
            <p style='color:#94a3b8; font-size:0.85rem;'>Simulates enterprise ATS filters across formatting, metrics, keywords, and action verbs.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_f2:
        st.markdown("""
        <div class='glass-card'>
            <h4>🔍 Skills Engine</h4>
            <p style='color:#94a3b8; font-size:0.85rem;'>Extracts and organizes 800+ skills across 10 domains including Cloud, AI, Security, and Backend.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_f3:
        st.markdown("""
        <div class='glass-card'>
            <h4>💼 Job Gap Match</h4>
            <p style='color:#94a3b8; font-size:0.85rem;'>TF-IDF & Cosine Similarity match against targeted job requirements with interactive simulator.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_f4:
        st.markdown("""
        <div class='glass-card'>
            <h4>🚀 XYZ Rewriter & Studio</h4>
            <p style='color:#94a3b8; font-size:0.85rem;'>Transforms passive bullets into Google's XYZ formula and exports ATS-formatted Word (.docx) files.</p>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# --- EXECUTE RESUME ANALYSIS PIPELINE ---
with st.spinner("Analyzing resume content, ATS signals, and skill taxonomies..."):
    sections = segment_sections(resume_text)
    skills_data = extract_skills(resume_text)
    analysis_data = analyze_full_resume(resume_text, sections, st.session_state.get("num_pages", 1))
    ats_score_data = calculate_ats_score(analysis_data, skills_data)

    # Job description comparison
    target_jd = st.session_state.get("target_jd", "")
    match_data = compare_resume_to_job(resume_text, target_jd)

    # Tailored suggestions
    suggestions_data = generate_tailored_suggestions(analysis_data, skills_data, match_data)

contact = analysis_data["contact"]
structure = analysis_data["structure"]
metrics = analysis_data["metrics"]
verbs = analysis_data["verbs"]


# --- CANDIDATE OVERVIEW HEADER ---
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
c_head1, c_head2 = st.columns([2, 1])

with c_head1:
    raw_name = st.session_state.get("resume_file_name", "Uploaded Resume").split(".")[0].replace("_", " ").title()
    candidate_name = raw_name
    st.markdown(f"<h3 style='margin-bottom:0.25rem;'>Candidate Profile: {candidate_name}</h3>", unsafe_allow_html=True)

    pills_html = "<div style='display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;'>"
    if contact.get("email"):
        pills_html += f"<span class='contact-pill'>📧 {contact['email']}</span>"
    if contact.get("phone"):
        pills_html += f"<span class='contact-pill'>📞 {contact['phone']}</span>"
    if contact.get("linkedin"):
        pills_html += f"<span class='contact-pill'>🔗 {contact['linkedin']}</span>"
    if contact.get("github"):
        pills_html += f"<span class='contact-pill'>💻 {contact['github']}</span>"
    pills_html += "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)

with c_head2:
    st.markdown(f"""
    <div style='text-align:right; font-size:0.85rem; color:#94a3b8; line-height:1.6;'>
        <b>Document:</b> {st.session_state.get('resume_file_name', 'Resume')}<br>
        <b>Word Count:</b> {structure['word_count']} words (~{structure['read_time_minutes']} min read)<br>
        <b>Status:</b> <span style='color:{ats_score_data["status_color"]}; font-weight:600;'>{ats_score_data['grade']} — {ats_score_data['verdict']}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# --- KPI METRICS ROW ---
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color:{ats_score_data["status_color"]};'>{ats_score_data["total_ats_score"]}</div>
        <div class='metric-label'>Overall ATS Score ({ats_score_data['grade']})</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    match_score = match_data["match_score"]
    m_color = "#10b981" if match_score >= 70 else ("#f59e0b" if match_score >= 45 else "#ef4444")
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color:{m_color};'>{match_score}%</div>
        <div class='metric-label'>Target Job Match</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color:#38bdf8;'>{len(skills_data['flat_skills'])}</div>
        <div class='metric-label'>Skills Detected</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color:#a855f7;'>{metrics['metric_count']}</div>
        <div class='metric-label'>Quantified Metrics</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- INTERACTIVE TABS ---
(
    tab_dash,
    tab_skills,
    tab_match,
    tab_xyz,
    tab_studio,
    tab_cover_letter,
    tab_benchmark,
    tab_critique
) = st.tabs([
    "📊 Executive Dashboard",
    "🔍 Skills Intelligence",
    "🎯 Target Job Match & Gap",
    "🚀 Google XYZ Bullet Rewriter",
    "📄 Live ATS Resume Studio",
    "✉️ Cover Letter & Outreach",
    "👥 Candidate Benchmarking",
    "🤖 Deep AI Critique & Star Prep"
])


# ==========================================
# TAB 1: EXECUTIVE DASHBOARD & ATS BREAKDOWN
# ==========================================
with tab_dash:
    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-bottom:0;'>ATS Score Benchmarks</h4>", unsafe_allow_html=True)
        gauge_fig = create_gauge_chart(ats_score_data["total_ats_score"], "ATS Pass Probability")
        st.plotly_chart(gauge_fig, use_container_width=True)

        st.markdown(f"""
        <div style='background:rgba(15, 23, 42, 0.4); padding:10px 14px; border-radius:8px; border-left:3px solid {ats_score_data["status_color"]};'>
            <b style='color:#f8fafc;'>Recruiter Verdict:</b> {ats_score_data["verdict"]}<br>
            <span style='font-size:0.85rem; color:#94a3b8;'>Scored based on structure, keywords, metrics, and active voice.</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-bottom:0;'>ATS Dimensional Balance</h4>", unsafe_allow_html=True)
        radar_fig = create_radar_chart(ats_score_data["breakdown"])
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Detailed component breakdown
    st.markdown("<div class='section-banner'>📋 Sub-Dimension Score Breakdown</div>", unsafe_allow_html=True)

    breakdown_items = ats_score_data["breakdown"]
    cols_b = st.columns(len(breakdown_items))
    for i, (cat_name, cat_info) in enumerate(breakdown_items.items()):
        with cols_b[i]:
            c_score = cat_info["score"]
            c_badge = "#10b981" if c_score >= 80 else ("#f59e0b" if c_score >= 55 else "#ef4444")
            st.markdown(f"""
            <div class='glass-card' style='text-align:center; padding:1rem 0.5rem;'>
                <div style='font-size:1.6rem; font-weight:700; color:{c_badge};'>{c_score}/100</div>
                <div style='font-weight:600; font-size:0.85rem; margin-top:4px;'>{cat_name}</div>
                <div style='font-size:0.75rem; color:#94a3b8; margin-top:4px;'>Weight: {int(cat_info['weight']*100)}%</div>
            </div>
            """, unsafe_allow_html=True)

    # Actionable ATS alerts
    if ats_score_data["feedback_notes"]:
        st.markdown("<div class='section-banner'>⚠️ Actionable ATS Observations</div>", unsafe_allow_html=True)
        for note in ats_score_data["feedback_notes"]:
            if note["type"] == "critical":
                st.error(f"🚨 **Critical**: {note['msg']}")
            elif note["type"] == "warning":
                st.warning(f"⚠️ **Warning**: {note['msg']}")
            else:
                st.info(f"💡 **Tip**: {note['msg']}")


# ==========================================
# TAB 2: SKILLS INTELLIGENCE
# ==========================================
with tab_skills:
    col_sk1, col_sk2 = st.columns([1, 1])

    with col_sk1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4>Skills Distribution Across Domains</h4>", unsafe_allow_html=True)
        cat_chart = create_category_bar_chart(skills_data["category_distribution"])
        st.plotly_chart(cat_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_sk2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4>Top Mentioned Skills & Frequencies</h4>", unsafe_allow_html=True)
        top_skills = sorted(skills_data["skill_frequencies"].items(), key=lambda x: x[1], reverse=True)[:10]
        if top_skills:
            df_top = pd.DataFrame(top_skills, columns=["Skill", "Mentions"])
            st.dataframe(
                df_top,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Skill": st.column_config.TextColumn("Technical Proficiency"),
                    "Mentions": st.column_config.ProgressColumn("Frequency in Document", min_value=0, max_value=max(1, top_skills[0][1]))
                }
            )
        else:
            st.info("No repeated skill mentions detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Search & Filter
    st.markdown("<div class='section-banner'>🗂️ Categorized Skill Inventory</div>", unsafe_allow_html=True)
    search_query = st.text_input("🔎 Search skills in your profile:", placeholder="e.g. Python, Docker, PyTorch, React...")

    found_by_cat = skills_data["found_by_category"]
    if found_by_cat:
        cat_cols = st.columns(2)
        idx = 0
        for category, skill_list in found_by_cat.items():
            filtered_skills = [s for s in skill_list if not search_query or search_query.lower() in s.lower()]
            if not filtered_skills:
                continue

            with cat_cols[idx % 2]:
                with st.expander(f"{category} ({len(filtered_skills)})", expanded=True):
                    badges = "".join([f"<span class='skill-badge badge-neutral'>{s}</span>" for s in filtered_skills])
                    st.markdown(f"<div class='badge-container'>{badges}</div>", unsafe_allow_html=True)
            idx += 1
    else:
        st.warning("No technical or soft skills detected from the skills taxonomy.")


# ==========================================
# TAB 3: TARGET JOB MATCH & GAP ANALYSIS
# ==========================================
with tab_match:
    st.markdown("<div class='section-banner'>🎯 Job Description Fit & Semantic Alignment</div>", unsafe_allow_html=True)

    col_jm1, col_jm2, col_jm3 = st.columns(3)
    with col_jm1:
        st.metric("Composite Job Match", f"{match_data['match_score']}%", help="Balanced blend of required skills present and semantic TF-IDF overlap.")
    with col_jm2:
        st.metric("Skill Coverage Ratio", f"{match_data['skill_match_ratio']}%", f"{len(match_data['matching_skills'])} of {len(match_data['jd_skills'])} JD skills")
    with col_jm3:
        st.metric("Semantic Similarity", f"{match_data['semantic_similarity']}%", "TF-IDF contextual overlap")

    col_m1, col_m2 = st.columns([1, 1])

    with col_m1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h4>✅ Matching Skills ({len(match_data['matching_skills'])})</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Skills requested in the job description that were discovered on your resume:</p>", unsafe_allow_html=True)
        if match_data["matching_skills"]:
            badges = "".join([f"<span class='skill-badge badge-match'>✓ {s}</span>" for s in match_data["matching_skills"]])
            st.markdown(f"<div class='badge-container'>{badges}</div>", unsafe_allow_html=True)
        else:
            st.info("No direct skill matches found between resume and job description.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h4>❌ Missing Keywords ({len(match_data['missing_skills'])})</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Skills demanded by the job description that are absent from your resume:</p>", unsafe_allow_html=True)
        if match_data["missing_skills"]:
            badges = "".join([f"<span class='skill-badge badge-missing'>+ {s}</span>" for s in match_data["missing_skills"]])
            st.markdown(f"<div class='badge-container'>{badges}</div>", unsafe_allow_html=True)
        else:
            st.success("🎉 Outstanding! You possess 100% of the skills requested in this job description.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Interactive Keyword Injection Simulator
    if match_data["missing_skills"]:
        st.markdown("<div class='section-banner'>🧪 Interactive ATS Score & Keyword Simulator</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Check the missing skills you have experience with to simulate your improved ATS & Job Match score in real time:</p>", unsafe_allow_html=True)

        selected_simulated = st.multiselect(
            "Select missing skills to simulate adding to your profile:",
            options=match_data["missing_skills"],
            default=st.session_state.get("simulated_added_skills", [])
        )
        st.session_state["simulated_added_skills"] = selected_simulated

        if selected_simulated:
            simulated_text = resume_text + "\nSkills: " + ", ".join(selected_simulated)
            sim_match = compare_resume_to_job(simulated_text, target_jd)
            sim_skills = extract_skills(simulated_text)
            sim_analysis = analyze_full_resume(simulated_text, sections)
            sim_ats = calculate_ats_score(sim_analysis, sim_skills)

            col_sim1, col_sim2 = st.columns(2)
            with col_sim1:
                st.success(f"📈 **Simulated Job Match Score:** {sim_match['match_score']}% (from {match_data['match_score']}%, **+{round(sim_match['match_score'] - match_data['match_score'], 1)}%**)")
            with col_sim2:
                st.success(f"📈 **Simulated Overall ATS Score:** {sim_ats['total_ats_score']}/100 (from {ats_score_data['total_ats_score']}, **+{round(sim_ats['total_ats_score'] - ats_score_data['total_ats_score'], 1)} pts**)")

    # Natural Integration Blueprint
    if suggestions_data["keyword_strategy"]:
        st.markdown("<div class='section-banner'>💡 Blueprint: How to Naturally Integrate Missing Skills</div>", unsafe_allow_html=True)
        for item in suggestions_data["keyword_strategy"]:
            st.markdown(f"""
            <div style='background:rgba(30, 41, 59, 0.4); border-left:3px solid #6366f1; padding:8px 14px; border-radius:6px; margin-bottom:8px;'>
                <b style='color:#a5b4fc;'>{item['skill']}:</b> {item['recommendation']}
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# TAB 4: GOOGLE XYZ FORMULA BULLET REWRITER
# ==========================================
with tab_xyz:
    st.markdown("<div class='section-banner'>📐 Google XYZ Formula Bullet Point Transformer</div>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#cbd5e1; font-size:0.9rem;'>
        Google recruiters famously evaluate bullet points using the <b>XYZ formula</b>: 
        <i>"Accomplished [X] as measured by [Y] by doing [Z]"</i>.
        Paste any weak or passive bullet from your resume below to generate 3 multi-style upgrades.
    </p>
    """, unsafe_allow_html=True)

    default_sample = (
        metrics["sample_impact_bullets"][0]
        if metrics.get("sample_impact_bullets")
        else "Worked on backend APIs and made database queries faster."
    )

    user_bullet_input = st.text_area(
        "Paste any bullet point to transform:",
        value=default_sample,
        height=70
    )

    col_btn_xyz, col_role_sel = st.columns([1, 2])
    with col_role_sel:
        target_role_hint = st.selectbox(
            "Target Role Archetype for Rewrite:",
            options=["Senior Full-Stack Engineer", "Senior Data Scientist / ML", "Cloud DevOps / Platform", "Frontend Specialist", "Engineering Manager"]
        )

    with col_btn_xyz:
        transform_btn = st.button("✨ Transform with XYZ Formula", use_container_width=True, type="primary")

    if transform_btn and user_bullet_input.strip():
        with st.spinner("Generating 3 multi-dimensional XYZ bullet upgrades..."):
            result_xyz = transform_bullet_point(
                bullet=user_bullet_input,
                target_role=target_role_hint,
                api_key=st.session_state.get("gemini_api_key", "")
            )
            st.session_state["last_xyz_result"] = result_xyz

    if "last_xyz_result" in st.session_state:
        xyz_data = st.session_state["last_xyz_result"]
        st.markdown(f"<p style='color:#94a3b8; font-size:0.85rem;'>Engine: <b>{xyz_data['source']}</b></p>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='border-left:4px solid #10b981;'>", unsafe_allow_html=True)
        st.markdown(xyz_data["content"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Reference Library
    with st.expander("📚 View Industry-Specific XYZ Formula Benchmark Examples", expanded=False):
        for template in suggestions_data["xyz_templates"]:
            st.markdown(f"""
            <div style='margin-bottom:12px; padding:10px; background:rgba(15, 23, 42, 0.5); border-radius:8px;'>
                <b style='color:#38bdf8;'>{template['role']}</b><br>
                <span style='color:#f87171;'>✖ Before:</span> <i>{template['before']}</i><br>
                <span style='color:#4ade80;'>✔ After:</span> <b>{template['after']}</b>
            </div>
            """, unsafe_allow_html=True)

    # Action Verbs Replacement Table
    st.markdown("<div class='section-banner'>🗣️ Action Verb Upgrades</div>", unsafe_allow_html=True)
    weak_verbs = verbs.get("weak_phrases_used", [])
    if weak_verbs:
        st.warning(f"Detected {len(weak_verbs)} passive phrase(s) in your resume: {', '.join(weak_verbs)}")
    else:
        st.success("No weak passive clichés detected! Your active voice is strong.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("**Weak Passive Cliché**")
        for weak in list(ACTION_VERB_REPLACEMENTS.keys())[:5]:
            st.markdown(f"• <span style='color:#f87171;'>{weak}</span>", unsafe_allow_html=True)
    with col_v2:
        st.markdown("**High-Impact Replacements**")
        for weak, strong_list in list(ACTION_VERB_REPLACEMENTS.items())[:5]:
            st.markdown(f"• **{', '.join(strong_list)}**")


# ==========================================
# TAB 5: LIVE ATS RESUME STUDIO & DOCX EXPORT
# ==========================================
with tab_studio:
    st.markdown("<div class='section-banner'>📄 Live ATS Resume Studio & Document Generator</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.9rem; color:#cbd5e1;'>Review and live-edit your resume sections. Click <b>Auto-Optimize</b> to automatically upgrade passive verbs, incorporate missing target keywords, and format bullets into an ATS-compliant Word (.docx) document.</p>", unsafe_allow_html=True)

    col_opt_btn, col_opt_info = st.columns([1, 2])
    with col_opt_btn:
        if st.button("⚡ Auto-Optimize Resume", use_container_width=True, type="primary"):
            st.session_state["optimized_sections"] = optimize_sections(
                sections=sections,
                missing_skills=match_data.get("missing_skills", []),
                weak_verbs=verbs.get("weak_phrases_used", [])
            )
            st.success("✓ Resume successfully optimized with upgraded action verbs and target keywords!")

    current_sections = st.session_state.get("optimized_sections") or sections

    # Section-by-section live editor
    edited_sections = {}
    sec_names = ["summary", "skills", "experience", "projects", "education", "certifications"]

    for sec in sec_names:
        if sec in current_sections:
            with st.expander(f"📝 {sec.upper()} Section", expanded=(sec in ["summary", "skills", "experience"])):
                val = current_sections[sec]
                edited_val = st.text_area(f"Edit {sec.title()}:", value=val, height=120, key=f"edit_sec_{sec}")
                edited_sections[sec] = edited_val

    # Any other custom sections
    for sec, val in current_sections.items():
        if sec not in sec_names and sec != "header":
            with st.expander(f"📝 {sec.upper()} Section", expanded=False):
                edited_val = st.text_area(f"Edit {sec.title()}:", value=val, height=100, key=f"edit_sec_{sec}")
                edited_sections[sec] = edited_val

    # Export Buttons
    st.markdown("<div class='section-banner'>💾 Export Formatted ATS Documents</div>", unsafe_allow_html=True)
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        docx_bytes = export_resume_to_docx(
            candidate_name=candidate_name,
            contact_info=contact,
            sections_dict=edited_sections
        )
        st.download_button(
            label="📥 Download ATS-Optimized Resume (.docx)",
            data=docx_bytes,
            file_name=f"{candidate_name.replace(' ', '_')}_Optimized_Resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    with col_dl2:
        markdown_resume = generate_full_resume_markdown(
            candidate_name=candidate_name,
            contact_info=contact,
            sections_dict=edited_sections
        )
        st.download_button(
            label="📥 Download Formatted Resume (.md)",
            data=markdown_resume,
            file_name=f"{candidate_name.replace(' ', '_')}_Optimized_Resume.md",
            mime="text/markdown",
            use_container_width=True
        )


# ==========================================
# TAB 6: COVER LETTER & RECRUITER OUTREACH
# ==========================================
with tab_cover_letter:
    st.markdown("<div class='section-banner'>✉️ Tailored Cover Letter & Recruiter InMail Outreach</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.9rem; color:#cbd5e1;'>Generate a high-converting cover letter and a punchy 150-word LinkedIn InMail pitch personalized to your background and the target job description.</p>", unsafe_allow_html=True)

    col_cl1, col_cl2 = st.columns(2)
    with col_cl1:
        target_company = st.text_input("Target Company Name:", value="Hiring Company")
    with col_cl2:
        target_role_title = st.text_input("Target Role Title:", value=preset_choice if preset_choice != "Custom Job Description" else "Senior Technology Specialist")

    if st.button("✨ Generate Custom Cover Letter & Pitch", use_container_width=True, type="primary"):
        with st.spinner("Drafting executive cover letter and recruiter pitch..."):
            cl_res = generate_cover_letter_and_pitch(
                candidate_name=candidate_name,
                resume_text=resume_text,
                jd_text=target_jd,
                company=target_company,
                job_title=target_role_title,
                api_key=st.session_state.get("gemini_api_key", "")
            )
            st.session_state["cover_letter_output"] = cl_res

    if "cover_letter_output" in st.session_state:
        cl_data = st.session_state["cover_letter_output"]
        st.markdown(f"<p style='color:#94a3b8; font-size:0.85rem;'>Engine: <b>{cl_data['source']}</b></p>", unsafe_allow_html=True)
        st.markdown(cl_data["content"])

        # DOCX Download
        cl_docx_bytes = export_cover_letter_to_docx(
            candidate_name=candidate_name,
            contact_info=contact,
            company=target_company,
            job_title=target_role_title,
            letter_text=cl_data["content"]
        )

        st.download_button(
            label="📥 Download Cover Letter as Word Document (.docx)",
            data=cl_docx_bytes,
            file_name=f"{candidate_name.replace(' ', '_')}_{target_company.replace(' ', '_')}_Cover_Letter.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )


# ==========================================
# TAB 7: CANDIDATE BENCHMARKING (RECRUITER MODE)
# ==========================================
with tab_benchmark:
    st.markdown("<div class='section-banner'>👥 Candidate Benchmarking & Competitive Ranking</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.9rem; color:#cbd5e1;'>Compare this candidate against peer candidate benchmarks for the target job description.</p>", unsafe_allow_html=True)

    # Prepare candidate pool
    candidates_pool = [
        {"name": f"{candidate_name} (Current)", "resume_text": resume_text}
    ]

    # Add sample profiles
    sample_fs_path = os.path.join("sample_resumes", "sample_software_engineer.docx")
    sample_ds_path = os.path.join("sample_resumes", "sample_data_scientist.pdf")

    if os.path.exists(sample_fs_path):
        with open(sample_fs_path, "rb") as f:
            fs_text = extract_text(f.read(), "sample_software_engineer.docx")["text"]
            candidates_pool.append({"name": "Alex Rivera (Senior FullStack)", "resume_text": fs_text})

    if os.path.exists(sample_ds_path):
        with open(sample_ds_path, "rb") as f:
            ds_text = extract_text(f.read(), "sample_data_scientist.pdf")["text"]
            candidates_pool.append({"name": "Dr. Priya Sharma (Data Scientist)", "resume_text": ds_text})

    comp_res = compare_candidates(candidates_pool, target_jd)

    # Comparative Metric Cards
    col_comp_lead1, col_comp_lead2 = st.columns(2)
    with col_comp_lead1:
        st.markdown(f"""
        <div class='glass-card' style='border-left:4px solid #10b981;'>
            <div class='leader-badge'>Top Role Fit Leader</div>
            <h3 style='margin-top:6px; margin-bottom:0;'>🏆 {comp_res['best_match_candidate']}</h3>
            <span style='font-size:0.85rem; color:#94a3b8;'>Highest skill alignment and semantic relevance to the job posting.</span>
        </div>
        """, unsafe_allow_html=True)

    with col_comp_lead2:
        st.markdown(f"""
        <div class='glass-card' style='border-left:4px solid #6366f1;'>
            <div class='leader-badge' style='background:linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);'>Top ATS Score Leader</div>
            <h3 style='margin-top:6px; margin-bottom:0;'>⭐ {comp_res['best_ats_candidate']}</h3>
            <span style='font-size:0.85rem; color:#94a3b8;'>Highest overall formatting, metrics density, and active voice score.</span>
        </div>
        """, unsafe_allow_html=True)

    # Leaderboard Table
    st.markdown("#### Candidate Leaderboard Table")
    df_comp = pd.DataFrame(comp_res["summary_table"])
    st.dataframe(df_comp, hide_index=True, use_container_width=True)

    # Charts
    col_cchart1, col_cchart2 = st.columns(2)
    with col_cchart1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4>Key Metrics Comparison</h4>", unsafe_allow_html=True)
        chart_bars = create_candidate_comparison_chart(comp_res["candidates_details"])
        st.plotly_chart(chart_bars, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cchart2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4>Dimensional Balance Overlay</h4>", unsafe_allow_html=True)
        chart_radars = create_multi_radar_comparison_chart(comp_res["candidates_details"])
        st.plotly_chart(chart_radars, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 8: DEEP AI CRITIQUE & STAR PREP
# ==========================================
with tab_critique:
    st.markdown("<div class='section-banner'>🤖 Deep Executive AI Critique & STAR Interview Prep</div>", unsafe_allow_html=True)

    current_key = st.session_state.get("gemini_api_key", "")
    is_live = is_gemini_available(current_key)

    if is_live:
        st.info("🟢 Gemini live model is configured and will generate an executive-level personalized critique.")
    else:
        st.info("🟡 Running on Intelligent Heuristic Engine. (Enter your Gemini API Key in the sidebar anytime for live Gemini analysis).")

    fallback_context = {
        "metrics": metrics,
        "verbs": verbs,
        "matching": match_data
    }

    if st.button("🚀 Run Deep AI Resume Evaluation", use_container_width=True, type="primary"):
        with st.spinner("Analyzing candidate background against executive hiring standards..."):
            critique_res = generate_gemini_critique(
                resume_text=resume_text,
                jd_text=target_jd,
                api_key=current_key,
                offline_fallback_data=fallback_context
            )
            st.session_state["critique_output"] = critique_res

    if "critique_output" in st.session_state:
        output_data = st.session_state["critique_output"]
        st.markdown(f"<p style='color:#94a3b8; font-size:0.85rem;'>Engine: <b>{output_data['source']}</b></p>", unsafe_allow_html=True)
        st.markdown(output_data["content"])

        # Export report option
        st.markdown("---")
        full_report = f"""# ElevateCV — Candidate ATS & AI Evaluation Report
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Candidate: {candidate_name}
File: {st.session_state.get('resume_file_name', 'Resume')}

## Summary Scores
- ATS Total Score: {ats_score_data['total_ats_score']} / 100 ({ats_score_data['grade']})
- Recruiter Verdict: {ats_score_data['verdict']}
- Job Match Score: {match_data['match_score']}%
- Total Skills Found: {len(skills_data['flat_skills'])}
- Quantifiable Metrics Found: {metrics['metric_count']}

## Skills Inventory
{', '.join(skills_data['flat_skills'])}

## Matching Skills for Target Role
{', '.join(match_data['matching_skills'])}

## Missing Target Keywords
{', '.join(match_data['missing_skills'])}

## Detailed AI Critique & Guidance
{output_data['content']}
"""
        st.download_button(
            label="📥 Download Full Analysis Audit Report (Markdown)",
            data=full_report,
            file_name=f"{candidate_name.replace(' ', '_')}_Full_ATS_Audit.md",
            mime="text/markdown",
            use_container_width=True
        )
