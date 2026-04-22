import streamlit as st
import pandas as pd
from utils.parser import extract_text_from_pdf
from utils.preprocess import clean_text
from utils.ranker import rank_resumes
from utils.skills import extract_skills

st.set_page_config(
    page_title="Recruiter AI Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS Styling
st.markdown(
    """<style>
/* Font */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}

/* Glassmorphism for Form Container */
div[data-testid="stForm"] {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}

/* Candidate Card Custom Styling - Glassmorphic */
.candidate-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-left: 5px solid var(--primary-color);
}
.candidate-card:hover {
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.15);
    transform: translateY(-4px);
    border: 1px solid var(--primary-color);
    border-left: 5px solid var(--primary-color);
}

.top-candidate {
    border-left: 5px solid #10b981;
    background: linear-gradient(135deg, var(--secondary-background-color) 0%, rgba(16, 185, 129, 0.05) 100%);
}
.top-candidate:hover {
    border: 1px solid #10b981;
    border-left: 5px solid #10b981;
}

.card-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 0.25rem;
}
.card-score {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary-color);
}
.top-candidate .card-score {
    color: #10b981;
}
.skill-badge {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 0.25rem;
    letter-spacing: 0.5px;
}
.badge-match {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.badge-miss {
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.badge-neutral {
    background-color: rgba(128, 128, 128, 0.1);
    color: var(--text-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
}

.explain-text {
    font-size: 0.9rem;
    color: var(--text-color);
    opacity: 0.8;
    margin-top: 1.2rem;
    padding-top: 1.2rem;
    border-top: 1px solid rgba(128, 128, 128, 0.2);
}

/* Premium Streamlit Input Overrides */
div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
    background-color: rgba(128, 128, 128, 0.05) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(128, 128, 128, 0.2) !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="input"] > div:hover, div[data-baseweb="textarea"] > div:hover, div[data-baseweb="select"] > div:hover {
    border-color: var(--primary-color) !important;
}
div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
    box-shadow: 0 0 0 1px var(--primary-color) !important;
    border-color: var(--primary-color) !important;
}

/* Premium Button */
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2) !important;
    padding: 0.5rem 1rem !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4) !important;
}
div[data-testid="stFormSubmitButton"] button p {
    color: white !important;
    font-weight: 600 !important;
}
</style>""",
    unsafe_allow_html=True
)

# Application Header
st.markdown("<h1>💼 AI Recruiter Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: var(--text-color); opacity: 0.7; font-size: 1.1rem; margin-bottom: 2rem;'>Smart candidate ranking and discovery dashboard powered by NLP.</p>", unsafe_allow_html=True)

# Layout: Form for inputs vs. Main Screen Columns
col1, col2 = st.columns([1.2, 2.8])

with col1:
    with st.form("job_details_form"):
        st.markdown("### 📝 Job Details")
        job_title = st.text_input("Job Title", placeholder="e.g. Senior Data Scientist")
        job_desc = st.text_area("Job Description", height=150, placeholder="Paste the full job description here...")
        
        st.markdown("### 🎯 Requirements")
        req_skills_str = st.text_input("Required Skills", placeholder="comma-separated (e.g. Python, SQL, AWS)")
        experience = st.number_input("Minimum Experience (Years)", min_value=0, max_value=30, value=0)
        
        st.markdown("### 📂 Resumes")
        uploaded_files = st.file_uploader("Upload Candidate Resumes (PDF)", accept_multiple_files=True, type=["pdf"])
        
        submit_btn = st.form_submit_button("🚀 Start Screening", use_container_width=True)

with col2:
    if submit_btn:
        if not uploaded_files:
            st.error("⚠️ Please upload at least one resume to proceed.")
        elif not job_desc:
            st.error("⚠️ Please provide a job description to score against.")
        else:
            with st.spinner("Analyzing candidates and generating insights..."):
                resumes_text = []
                names = []
                all_skills_extracted = []
                
                # Parse customized requirement skills
                required_skills = [s.strip().lower() for s in req_skills_str.split(',')] if req_skills_str else []
                required_skills = [s for s in required_skills if s] # Clean empty strings
                
                # Extract basic skills from JD using predefined skills
                job_clean = clean_text(job_desc)
                jd_skills = extract_skills(job_clean)
                
                # Merge user requirements and JD skills, removing duplicates
                combined_req_skills = list(set(required_skills + jd_skills))

                for file in uploaded_files:
                    text = extract_text_from_pdf(file)
                    clean = clean_text(text)
                    
                    # Extract predefined skills from resume
                    cand_skills = extract_skills(clean)
                    
                    # For custom skills the user explicitly typed, manual check them via string matching
                    for r_skill in required_skills:
                        if r_skill and r_skill not in cand_skills:
                            if r_skill in clean:
                                cand_skills.append(r_skill)
                    
                    cand_skills = list(set(cand_skills))
                    
                    resumes_text.append(clean)
                    names.append(file.name)
                    all_skills_extracted.append(cand_skills)

                scores = rank_resumes(resumes_text, job_clean)
                
                candidates_data = []

                for name, sim_score, skills in zip(names, scores, all_skills_extracted):
                    # Skill match based on Combined Required Skills
                    if combined_req_skills:
                        matched_skills = list(set(skills) & set(combined_req_skills))
                        missing_skills = list(set(combined_req_skills) - set(skills))
                        skill_score = len(matched_skills) / len(combined_req_skills)
                    else:
                        matched_skills = []
                        missing_skills = []
                        skill_score = 0.0
                    
                    # New Weighting: 60% Text Similarity, 40% Skill match
                    final_score = (sim_score * 0.6) + (skill_score * 0.4)
                    
                    # Explainability Reasoning
                    if final_score > 0.7:
                        reason = "Strong candidate: High contextual similarity to the job description and solid skills overlap."
                    elif final_score > 0.4:
                        reason = "Potential match: Moderate relevance, but may require upskilling in missing areas."
                    else:
                        reason = "Weak match: Lacks core competencies and context alignment with the role."

                    candidates_data.append({
                        "Name": name.replace(".pdf", ""),
                        "Score": round(final_score * 100, 1),
                        "Similarity Score": round(sim_score * 100, 1),
                        "Skill Score": round(skill_score * 100, 1),
                        "Matched Skills": matched_skills,
                        "Missing Skills": missing_skills,
                        "Explanation": reason
                    })

                df = pd.DataFrame(candidates_data)
                df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
                df.index = df.index + 1  # 1-based ranking

                # ====== DASHBOARD DISPLAY ======
                
                st.markdown("### 📊 Screening Dashboard")
                
                # Top Level Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Candidates Evaluated", len(df))
                m2.metric("Average Score", f"{df['Score'].mean():.1f}%")
                m3.metric("Critical Skills Identified", len(combined_req_skills))

                st.markdown("---")
                
                # Tabbed View for detailed inspection
                tab1, tab2 = st.tabs(["🏆 Top Candidates", "📋 Full Ranking Table"])
                
                with tab1:
                    for i in range(min(5, len(df))):
                        row = df.iloc[i]
                        
                        is_top = (i == 0)
                        card_class = "candidate-card top-candidate" if is_top else "candidate-card"
                        medal = "🥇 Top Match" if is_top else f"Rank #{i+1}"
                        
                        match_badges = " ".join([f'<span class="skill-badge badge-match">{skill}</span>' for skill in row['Matched Skills']])
                        miss_badges = " ".join([f'<span class="skill-badge badge-miss">{skill}</span>' for skill in row['Missing Skills'][:5]])
                        if len(row['Missing Skills']) > 5:
                            miss_badges += f'<span class="skill-badge badge-miss">+{len(row["Missing Skills"])-5} more</span>'
                        
                        if not match_badges: match_badges = "<span class='skill-badge badge-neutral'>None Detected</span>"
                        if not miss_badges: miss_badges = "<span class='skill-badge badge-neutral'>None</span>"

                        card_html = f"""<div class="{card_class}">
<div style="display: flex; justify-content: space-between; align-items: start;">
<div>
<div style="color: var(--text-color); opacity: 0.7; font-size: 0.875rem; font-weight: 600; text-transform: uppercase;">{medal}</div>
<div class="card-title">{row['Name']}</div>
</div>
<div class="card-score">{row['Score']}%</div>
</div>
<div style="margin-top: 12px;">
<span style="font-size: 0.875rem; font-weight: 600; color: var(--text-color); opacity: 0.85;">✓ Matched Capabilities:</span><br>
{match_badges}
</div>
<div style="margin-top: 12px;">
<span style="font-size: 0.875rem; font-weight: 600; color: var(--text-color); opacity: 0.85;">✗ Missing Capabilities:</span><br>
{miss_badges}
</div>
<div class="explain-text">
<strong>💡 AI Insights:</strong> {row['Explanation']} <br>
<em>(JD Similarity: {row['Similarity Score']}% | Skills Match: {row['Skill Score']}%)</em>
</div>
</div>"""
                        st.markdown(card_html, unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("#### Complete Candidate Pool")
                    # Formatting dataframe nicely
                    display_df = df.copy()
                    display_df['Matched Skills'] = display_df['Matched Skills'].apply(lambda x: ", ".join(x) if x else "None")
                    display_df['Missing Skills'] = display_df['Missing Skills'].apply(lambda x: ", ".join(x) if x else "None")
                    
                    st.dataframe(
                        display_df[['Name', 'Score', 'Similarity Score', 'Skill Score', 'Matched Skills', 'Missing Skills', 'Explanation']],
                        use_container_width=True,
                        hide_index=False
                    )

    else:
        # Empty state dashboard illustration
        empty_html = """<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding-top: 6rem;">
<div style="font-size: 5rem; margin-bottom: 1rem;">🔍</div>
<h3 style="color: var(--text-color); font-weight: 600;">Ready to screen candidates</h3>
<p style="color: var(--text-color); opacity: 0.7; text-align: center; max-width: 400px;">
Fill out the job details and upload candidate resumes on the left to instantly generate a ranking dashboard.
</p>
</div>"""
        st.markdown(empty_html, unsafe_allow_html=True)
