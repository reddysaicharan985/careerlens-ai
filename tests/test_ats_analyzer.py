from services.ats_analyzer import analyze_ats_readiness
from services.job_schema import JobRequirements


def test_ats_readiness_rewards_complete_relevant_resume():
    resume_text = """
    Professional Summary
    AI engineering student with practical project experience.

    Technical Skills
    Python, FastAPI, REST APIs, LangChain and Git.

    Experience
    Developed and tested AI services for document processing.

    Education
    B.Tech in Computer Science and Artificial Intelligence, 2027.

    Projects
    Built and deployed 3 AI projects and improved retrieval
    performance by 25%.
    """

    job_requirements = JobRequirements(
        job_title="AI Engineer Intern",
        required_skills=[
            "Python",
            "FastAPI",
        ],
        important_keywords=[
            "REST APIs",
        ],
    )

    result = analyze_ats_readiness(
        resume_text=resume_text,
        page_count=1,
        job_requirements=job_requirements,
    )

    assert result.overall_score >= 80
    assert result.parseability_score == 20
    assert result.section_score == 25
    assert result.keyword_score == 35
    assert "Python" in result.matched_keywords
    assert "FastAPI" in result.matched_keywords
    assert result.missing_keywords == []


def test_ats_readiness_identifies_missing_sections_and_keywords():
    resume_text = (
        "Education\n"
        "B.Tech student completing general academic coursework. "
        * 20
    )

    job_requirements = JobRequirements(
        job_title="AI Engineer Intern",
        required_skills=[
            "Python",
            "FastAPI",
            "Docker",
        ],
    )

    result = analyze_ats_readiness(
        resume_text=resume_text,
        page_count=1,
        job_requirements=job_requirements,
    )

    assert result.overall_score < 50
    assert "Skills" in result.missing_sections
    assert "Experience" in result.missing_sections
    assert "Projects" in result.missing_sections
    assert "Python" in result.missing_keywords
    assert "FastAPI" in result.missing_keywords
    assert result.recommendations