from services.job_schema import JobRequirements
from services.local_resume_matcher import (
    match_resume_to_job_local,
)


def test_matches_supported_skills_and_keeps_missing_separate():
    resume_text = """
    Professional Summary
    B.Tech Computer Science student graduating in 2027.

    Technical Skills
    Python, LangChain, GitHub, ChromaDB and Streamlit.

    Projects
    Built a Retrieval-Augmented Generation application using
    Python, LangChain and ChromaDB. Deployed the application
    with Streamlit and documented the project on GitHub.
    """

    requirements = JobRequirements(
        job_title="AI Engineer Intern",
        required_skills=[
            "Python",
            "FastAPI",
            "LangChain",
        ],
        preferred_skills=[
            "GitHub",
            "Docker",
        ],
        education=[
            "B.Tech in Computer Science",
        ],
        experience_level="Freshers and students",
    )

    result = match_resume_to_job_local(
        resume_text,
        requirements,
    )

    matched_required = [
        item.skill
        for item in result.matched_required_skills
    ]

    matched_preferred = [
        item.skill
        for item in result.matched_preferred_skills
    ]

    assert "Python" in matched_required
    assert "LangChain" in matched_required
    assert "FastAPI" in result.missing_required_skills
    assert "GitHub" in matched_preferred
    assert "Docker" not in matched_preferred
    assert result.education_match is True
    assert result.experience_match is True
    assert result.summary


def test_recognizes_skill_aliases():
    resume_text = """
    Technical Skills
    GenAI, LLMs, RAG, vector stores and prompt engineering.

    Projects
    Developed a retrieval augmented generation system with
    semantic search and grounded answers for PDF documents.
    The project contains tested Python modules and documentation.
    """

    requirements = JobRequirements(
        required_skills=[
            "Generative AI",
            "Large Language Models",
            "Retrieval-Augmented Generation",
            "Prompt Engineering",
        ],
    )

    result = match_resume_to_job_local(
        resume_text,
        requirements,
    )

    matched = {
        item.skill
        for item in result.matched_required_skills
    }

    assert matched == {
        "Generative AI",
        "Large Language Models",
        "Retrieval-Augmented Generation",
        "Prompt Engineering",
    }
    assert result.missing_required_skills == []


def test_does_not_invent_unsupported_skills():
    resume_text = """
    Education
    B.Tech Computer Science student.

    Projects
    Built responsive HTML and CSS pages using JavaScript.
    Used Firebase for authentication and database operations.
    Documented the implementation and tested the user interface.
    """

    requirements = JobRequirements(
        required_skills=[
            "Python",
            "FastAPI",
            "Docker",
        ],
    )

    result = match_resume_to_job_local(
        resume_text,
        requirements,
    )

    assert result.matched_required_skills == []
    assert result.missing_required_skills == [
        "Python",
        "FastAPI",
        "Docker",
    ]