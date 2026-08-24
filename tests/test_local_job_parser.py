import pytest

from services.local_job_parser import (
    parse_job_description_local,
)


def test_parses_structured_ai_engineer_description():
    job_description = """
    Job Title: AI Engineer Intern
    Company: InnovateAI Technologies
    Location: Hyderabad, Telangana
    Employment Type: Internship

    Responsibilities:
    - Build retrieval systems for internal documents.
    - Develop secure backend services.
    - Test and document AI features.

    Required Skills:
    - Python
    - FastAPI
    - Retrieval-Augmented Generation
    - LangChain
    - REST APIs

    Preferred Skills:
    - Docker
    - AWS

    Qualifications:
    - Pursuing a B.Tech degree in Computer Science.
    - Freshers and students may apply.
    """

    result = parse_job_description_local(job_description)

    assert result.job_title == "AI Engineer Intern"
    assert result.company_name == "InnovateAI Technologies"
    assert result.location == "Hyderabad, Telangana"
    assert result.employment_type == "Internship"
    assert "Python" in result.required_skills
    assert "FastAPI" in result.required_skills
    assert "LangChain" in result.required_skills
    assert "Docker" in result.preferred_skills
    assert "AWS" in result.preferred_skills
    assert result.responsibilities
    assert result.education
    assert result.important_keywords


def test_uses_not_specified_for_unavailable_fields():
    job_description = """
    We are looking for a motivated candidate to build and test
    Python applications. The candidate will use Git and SQL,
    document their work, collaborate with developers and solve
    practical software-engineering problems.
    """

    result = parse_job_description_local(job_description)

    assert result.company_name == "Not specified"
    assert result.location == "Not specified"
    assert "Python" in result.required_skills
    assert "Git" in result.required_skills
    assert "SQL" in result.required_skills


def test_rejects_short_job_description():
    with pytest.raises(
        ValueError,
        match="at least 80 characters",
    ):
        parse_job_description_local("Python internship")