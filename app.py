import streamlit as st

from services.job_parser import parse_job_description
from services.privacy import redact_personal_data
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
    "CareerLens will analyze your suitability, identify "
    "skill gaps and prepare personalized application material."
)

st.info(
    "Current milestone: privacy-protected resume extraction "
    "and structured AI job-description analysis."
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

analyze_button = st.button(
    "Analyze Job Match",
    type="primary",
    use_container_width=True,
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
                "Resume protected and job description analyzed!"
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

            type_column, level_column = st.columns(2)

            type_column.markdown("**Employment type**")
            type_column.write(job_requirements.employment_type)

            level_column.markdown("**Experience level**")
            level_column.write(job_requirements.experience_level)

            skill_column, responsibility_column = st.columns(2)

            with skill_column:
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

            with responsibility_column:
                st.markdown("**Responsibilities**")

                if job_requirements.responsibilities:
                    for responsibility in (
                        job_requirements.responsibilities
                    ):
                        st.markdown(f"- {responsibility}")
                else:
                    st.write("No responsibilities were specified.")

            with st.expander("Important ATS keywords"):
                if job_requirements.important_keywords:
                    st.write(
                        ", ".join(
                            job_requirements.important_keywords
                        )
                    )
                else:
                    st.write("No ATS keywords were identified.")

            with st.expander(
                "Preview privacy-protected resume text"
            ):
                st.text_area(
                    "Privacy-protected text",
                    value=safe_resume_text,
                    height=350,
                    disabled=True,
                )

            st.info(
                "The resume has not been matched yet. "
                "The next milestone will compare the protected "
                "resume with these validated job requirements."
            )