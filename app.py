import streamlit as st

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
    "Current milestone: local resume extraction and privacy protection. "
    "No information is being sent to an AI model yet."
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
            with st.spinner("Reading your resume..."):
                resume_text, page_count = extract_resume_text(
                    resume_file
                )

        except ValueError as error:
            st.error(str(error))

        except Exception:
            st.error(
                "CareerLens could not process this PDF. "
                "Please try another text-based resume."
            )

        else:
            safe_resume_text, redaction_counts = (
                redact_personal_data(resume_text)
            )
            total_redactions = sum(redaction_counts.values())

            st.success("Resume extracted successfully!")

            column1, column2, column3, column4 = st.columns(4)

            column1.metric(
                "Resume pages",
                page_count,
            )

            column2.metric(
                "Resume characters",
                len(resume_text),
            )

            column3.metric(
                "Job-description characters",
                len(job_description),
            )

            column4.metric(
                "Private details removed",
                total_redactions,
            )

            with st.expander(
                "Preview privacy-protected resume text"
            ):
                st.text_area(
                    "Privacy-protected text",
                    value=safe_resume_text,
                    height=350,
                    disabled=True,
                )

            st.success(
                "The displayed resume text is ready for AI processing. "
                "Direct contact details have been removed."
            )