import streamlit as st

from agent import careerlens_agent
from services.privacy import redact_personal_data
from tools.resume_tool import extract_resume_text


st.set_page_config(
    page_title="CareerLens AI",
    page_icon="🎯",
    layout="wide",
)

if "career_analysis" not in st.session_state:
    st.session_state.career_analysis = None

st.title("CareerLens AI")
st.subheader(
    "Agentic Job Research and Resume Matching Assistant"
)

st.write(
    "Upload your resume and paste a job description. "
    "CareerLens will compare your evidence with the role, "
    "calculate a transparent score and choose the next action."
)

st.info(
    "Agentic milestone: LangGraph routes suitable matches "
    "to application preparation and lower matches to a "
    "targeted learning plan."
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
    "Run CareerLens Agent",
    type="primary",
    use_container_width=True,
    disabled=not consent_given,
)

if not consent_given:
    st.caption(
        "Review the privacy notice and provide consent "
        "to enable the CareerLens agent."
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

            with st.spinner(
                "CareerLens Agent is analyzing and choosing "
                "the next action..."
            ):
                agent_result = careerlens_agent.invoke(
                    {
                        "safe_resume_text": safe_resume_text,
                        "job_description": job_description.strip(),
                    }
                )

            st.session_state.career_analysis = {
                "agent_result": agent_result,
                "resume_text": resume_text,
                "safe_resume_text": safe_resume_text,
                "page_count": page_count,
                "redaction_counts": redaction_counts,
                "job_description": job_description.strip(),
            }

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(
                "CareerLens Agent could not complete the workflow. "
                f"Technical details: {error}"
            )


analysis = st.session_state.career_analysis

if analysis is not None:
    agent_result = analysis["agent_result"]
    resume_text = analysis["resume_text"]
    safe_resume_text = analysis["safe_resume_text"]
    page_count = analysis["page_count"]
    redaction_counts = analysis["redaction_counts"]
    analyzed_job_description = analysis["job_description"]

    job_requirements = agent_result["job_requirements"]
    match_analysis = agent_result["match_analysis"]
    match_score = agent_result["match_score"]

    total_redactions = sum(redaction_counts.values())

    st.success("CareerLens Agent completed the workflow!")

    column1, column2, column3, column4 = st.columns(4)

    column1.metric("Resume pages", page_count)
    column2.metric("Resume characters", len(resume_text))
    column3.metric(
        "Job-description characters",
        len(analyzed_job_description),
    )
    column4.metric(
        "Private details removed",
        total_redactions,
    )

    st.subheader("Match result")

    score_column, recommendation_column = st.columns([1, 3])

    score_column.metric(
        "Overall match",
        f"{match_score.overall_score}%",
    )

    recommendation_column.markdown("**Recommendation**")
    recommendation_column.write(match_score.recommendation)

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
            for item in match_analysis.matched_required_skills:
                st.markdown(f"**{item.skill}**")
                st.caption(item.evidence)
        else:
            st.write(
                "No required skills were supported by resume evidence."
            )

    with missing_column:
        st.markdown("### Missing required skills")

        if match_analysis.missing_required_skills:
            for skill in match_analysis.missing_required_skills:
                st.markdown(f"- {skill}")
        else:
            st.write("No required skill gaps were identified.")

    st.divider()

    if "application_materials" in agent_result:
        materials = agent_result["application_materials"]

        st.subheader("Agent decision: Prepare application")
        st.success(
            "The score met the application threshold, so the "
            "agent prepared role-specific application materials."
        )

        st.markdown("### Application email subject")
        st.code(materials.email_subject, language=None)

        st.markdown("### Application email")
        st.text_area(
            "Generated email",
            value=materials.email_body,
            height=250,
            disabled=True,
        )

        st.download_button(
            "Download application email",
            data=(
                f"Subject: {materials.email_subject}\n\n"
                f"{materials.email_body}"
            ),
            file_name="careerlens_application_email.txt",
            mime="text/plain",
        )

        st.markdown("### Cover letter")
        st.text_area(
            "Generated cover letter",
            value=materials.cover_letter,
            height=400,
            disabled=True,
        )

        st.download_button(
            "Download cover letter",
            data=materials.cover_letter,
            file_name="careerlens_cover_letter.txt",
            mime="text/plain",
        )

        with st.expander("Interview preparation focus"):
            if materials.interview_focus:
                for topic in materials.interview_focus:
                    st.markdown(f"- {topic}")
            else:
                st.write("No interview topics were generated.")

    elif "learning_plan" in agent_result:
        learning_plan = agent_result["learning_plan"]

        st.subheader("Agent decision: Create learning plan")
        st.warning(
            "The score was below the application threshold, "
            "so the agent prepared a targeted improvement plan."
        )

        for step_number, step in enumerate(
            learning_plan.priority_steps,
            start=1,
        ):
            with st.expander(
                f"Step {step_number}: {step.skill}",
                expanded=step_number == 1,
            ):
                st.markdown("**Why it matters**")
                st.write(step.reason)
                st.markdown("**Actions**")

                for action in step.actions:
                    st.markdown(f"- {action}")

                st.markdown("**Proof project**")
                st.write(step.proof_project)

        st.markdown("### Suggested portfolio project")
        st.write(learning_plan.suggested_project)

        st.markdown("### Readiness note")
        st.write(learning_plan.readiness_note)

    st.divider()
    st.subheader("Structured job analysis")

    role_column, company_column, location_column = st.columns(3)

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
                ", ".join(job_requirements.important_keywords)
            )
        else:
            st.write("No ATS keywords were identified.")

    with st.expander("Preview the resume text sent to Gemini"):
        st.text_area(
            "Privacy-protected resume text",
            value=safe_resume_text,
            height=350,
            disabled=True,
        )

    if st.button("Clear analysis results"):
        st.session_state.career_analysis = None
        st.rerun()

    st.caption(
        "CareerLens provides decision support, not a hiring "
        "guarantee. Always review generated materials before use."
    )