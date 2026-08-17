import streamlit as st

from services.job_parser import parse_job_description
from services.privacy import redact_personal_data
from services.resume_matcher import match_resume_to_job
from services.scoring import calculate_match_score
from tools.resume_tool import extract_resume_text


st.set_page_config(
    page_title="CareerLens AI",
    page_icon="🎯",
    layout="wide",
)

st.title("CareerLens AI")
st.subheader(
    "Agentic Job Research and Resume Matching Assistant"
)

st.write(
    "Upload your resume and paste a job description. "
    "CareerLens will compare your evidence with the role, "
    "identify skill gaps and provide an honest recommendation."
)

st.info(
    "Current milestone: privacy-protected, evidence-based "
    "resume-to-job matching with transparent scoring."
)

st.divider()

resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf"],
    help="Only PDF resumes are accepted.",
)

job_description = st.text_area(
    "Paste the complete job description",
    height=300,
    placeholder=(
        "Example:\n"
        "Job title: AI Engineer Intern\n"
        "Required skills: Python, RAG, LangChain..."
    ),
)

st.warning(
    "Privacy notice: CareerLens removes email addresses, "
    "phone numbers and URLs before matching. The remaining "
    "resume content—including your name, city, education, "
    "skills, experience and projects—may be sent to Gemini."
)

consent_given = st.checkbox(
    "I understand and consent to sending the "
    "privacy-protected resume text to Gemini for matching."
)

analyze_button = st.button(
    "Analyze Job Match",
    type="primary",
    use_container_width=True,
    disabled=not consent_given,
)

if not consent_given:
    st.caption(
        "Review the privacy notice and provide consent "
        "to enable resume matching."
    )

if analyze_button:
    if resume_file is None:
        st.error("Please upload your resume PDF.")

    elif not job_description.strip():
        st.error("Please paste the job description.")

    elif len(job_description.strip()) < 100:
        st.warning(
            "The job description is very short. "
            "Please paste the complete description."
        )

    else:
        try:
            with st.spinner("Reading and protecting your resume..."):
                resume_text, page_count = extract_resume_text(
                    resume_file
                )
                safe_resume_text, redaction_counts = (
                    redact_personal_data(resume_text)
                )

            with st.spinner("Structuring the job requirements..."):
                job_requirements = parse_job_description(
                    job_description
                )

            with st.spinner("Matching resume evidence to the role..."):
                match_analysis = match_resume_to_job(
                    safe_resume_text,
                    job_requirements,
                )

            match_score = calculate_match_score(
                job_requirements,
                match_analysis,
            )

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(
                "CareerLens could not complete the analysis. "
                f"Technical details: {error}"
            )

        else:
            total_redactions = sum(redaction_counts.values())

            st.success(
                "Resume protected and job match completed!"
            )

            column1, column2, column3, column4 = st.columns(4)

            column1.metric("Resume pages", page_count)
            column2.metric("Resume characters", len(resume_text))
            column3.metric(
                "Job-description characters",
                len(job_description),
            )
            column4.metric(
                "Private details removed",
                total_redactions,
            )

            st.subheader("Match result")

            score_column, recommendation_column = st.columns(
                [1, 3]
            )

            score_column.metric(
                "Overall match",
                f"{match_score.overall_score}%",
            )

            recommendation_column.markdown("**Recommendation**")
            recommendation_column.write(
                match_score.recommendation
            )

            st.progress(match_score.overall_score / 100)
            st.write(match_analysis.summary)

            component_columns = st.columns(4)

            component_columns[0].metric(
                "Required skills",
                (
                    f"{match_score.required_skill_score}%"
                    if match_score.required_skill_score is not None
                    else "N/A"
                ),
            )

            component_columns[1].metric(
                "Preferred skills",
                (
                    f"{match_score.preferred_skill_score}%"
                    if match_score.preferred_skill_score is not None
                    else "N/A"
                ),
            )

            component_columns[2].metric(
                "Education",
                (
                    f"{match_score.education_score}%"
                    if match_score.education_score is not None
                    else "N/A"
                ),
            )

            component_columns[3].metric(
                "Experience",
                (
                    f"{match_score.experience_score}%"
                    if match_score.experience_score is not None
                    else "N/A"
                ),
            )

            matched_column, missing_column = st.columns(2)

            with matched_column:
                st.markdown("### Matched required skills")

                if match_analysis.matched_required_skills:
                    for item in (
                        match_analysis.matched_required_skills
                    ):
                        st.markdown(f"**{item.skill}**")
                        st.caption(item.evidence)
                else:
                    st.write(
                        "No required skills were supported "
                        "by resume evidence."
                    )

            with missing_column:
                st.markdown("### Missing required skills")

                if match_analysis.missing_required_skills:
                    for skill in (
                        match_analysis.missing_required_skills
                    ):
                        st.markdown(f"- {skill}")
                else:
                    st.write(
                        "No required skill gaps were identified."
                    )

            transferable_column, improvement_column = st.columns(2)

            with transferable_column:
                st.markdown("### Transferable skills")

                if match_analysis.transferable_skills:
                    for item in match_analysis.transferable_skills:
                        st.markdown(f"**{item.skill}**")
                        st.caption(item.evidence)
                else:
                    st.write(
                        "No additional transferable skills "
                        "were identified."
                    )

            with improvement_column:
                st.markdown("### Improvement areas")

                if match_analysis.improvement_areas:
                    for area in match_analysis.improvement_areas:
                        st.markdown(f"- {area}")
                else:
                    st.write(
                        "No immediate improvement areas "
                        "were identified."
                    )

            with st.expander("Candidate strengths"):
                if match_analysis.strengths:
                    for strength in match_analysis.strengths:
                        st.markdown(f"- {strength}")
                else:
                    st.write("No strengths were identified.")

            with st.expander("Education and experience evidence"):
                st.markdown("**Education**")
                st.write(match_analysis.education_evidence)
                st.markdown("**Experience**")
                st.write(match_analysis.experience_evidence)

            st.divider()
            st.subheader("Structured job analysis")

            role_column, company_column, location_column = (
                st.columns(3)
            )

            role_column.markdown("**Job title**")
            role_column.write(job_requirements.job_title)

            company_column.markdown("**Company**")
            company_column.write(job_requirements.company_name)

            location_column.markdown("**Location**")
            location_column.write(job_requirements.location)

            with st.expander("Job requirements and ATS keywords"):
                st.markdown("**Required skills**")

                if job_requirements.required_skills:
                    for skill in job_requirements.required_skills:
                        st.markdown(f"- {skill}")
                else:
                    st.write("No required skills were specified.")

                st.markdown("**Preferred skills**")

                if job_requirements.preferred_skills:
                    for skill in job_requirements.preferred_skills:
                        st.markdown(f"- {skill}")
                else:
                    st.write("No preferred skills were specified.")

                st.markdown("**Important ATS keywords**")

                if job_requirements.important_keywords:
                    st.write(
                        ", ".join(
                            job_requirements.important_keywords
                        )
                    )
                else:
                    st.write("No ATS keywords were identified.")

            with st.expander(
                "Preview the text that was sent for matching"
            ):
                st.text_area(
                    "Privacy-protected resume text",
                    value=safe_resume_text,
                    height=350,
                    disabled=True,
                )

            st.caption(
                "CareerLens provides decision support, not a hiring "
                "guarantee. Always review the original job post."
            )