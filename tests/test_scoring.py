from services.job_schema import JobRequirements
from services.match_schema import (
    ResumeMatchAnalysis,
    SkillEvidence,
)
from services.scoring import calculate_match_score


def test_partial_required_skill_match():
    job = JobRequirements(
        required_skills=[
            "Python",
            "RAG",
            "FastAPI",
        ]
    )

    analysis = ResumeMatchAnalysis(
        matched_required_skills=[
            SkillEvidence(
                skill="Python",
                evidence="Python project experience",
            ),
            SkillEvidence(
                skill="RAG",
                evidence="Built a RAG assistant",
            ),
        ],
        missing_required_skills=["FastAPI"],
        summary="Two of three required skills are supported.",
    )

    score = calculate_match_score(job, analysis)

    assert score.overall_score == 67
    assert score.required_skill_score == 67
    assert score.preferred_skill_score is None
    assert score.recommendation == (
        "Moderate match — apply and address the gaps"
    )


def test_complete_job_match():
    job = JobRequirements(
        experience_level="Project experience",
        required_skills=["Python", "RAG"],
        preferred_skills=["LangChain"],
        education=["B.Tech in Computer Science"],
    )

    analysis = ResumeMatchAnalysis(
        matched_required_skills=[
            SkillEvidence(
                skill="Python",
                evidence="Python project experience",
            ),
            SkillEvidence(
                skill="RAG",
                evidence="Built and deployed a RAG assistant",
            ),
        ],
        matched_preferred_skills=[
            SkillEvidence(
                skill="LangChain",
                evidence="Used LangChain in the RAG project",
            )
        ],
        education_match=True,
        education_evidence="B.Tech CSE–AI & ML student",
        experience_match=True,
        experience_evidence="Project-based AI development",
        summary="All stated requirements are supported.",
    )

    score = calculate_match_score(job, analysis)

    assert score.overall_score == 100
    assert score.required_skill_score == 100
    assert score.preferred_skill_score == 100
    assert score.education_score == 100
    assert score.experience_score == 100
    assert score.recommendation == "Strong match — apply"