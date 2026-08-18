from services import action_generator
from services.action_schema import (
    ApplicationMaterials,
    LearningPlan,
)
from services.job_schema import JobRequirements
from services.match_schema import ResumeMatchAnalysis
from services.scoring import MatchScore


class FakeStructuredModel:
    def __init__(self, response):
        self.response = response

    def invoke(self, messages):
        return self.response


class FakeModel:
    def __init__(self, response):
        self.response = response

    def with_structured_output(self, **kwargs):
        return FakeStructuredModel(self.response)


def create_job_requirements():
    return JobRequirements(
        job_title="AI Engineer Intern",
        company_name="Test Company",
        required_skills=["Python", "LangChain"],
    )


def create_match_analysis():
    return ResumeMatchAnalysis(
        missing_required_skills=["LangChain"],
        summary="The candidate needs additional LangChain experience.",
    )


def create_match_score(score):
    return MatchScore(
        overall_score=score,
        recommendation="Test recommendation",
        required_skill_score=50,
        preferred_skill_score=None,
        education_score=None,
        experience_score=None,
    )


def test_generates_valid_application_materials(monkeypatch):
    response = {
        "email_subject": "Application for AI Engineer Intern",
        "email_body": "I am applying for the internship.",
        "cover_letter": "I have project-level Python experience.",
        "interview_focus": ["Python", "RAG"],
    }

    monkeypatch.setattr(
        action_generator,
        "create_gemini_model",
        lambda: FakeModel(response),
    )

    result = action_generator.generate_application_materials(
        "Python and RAG project experience",
        create_job_requirements(),
        create_match_analysis(),
        create_match_score(60),
    )

    assert isinstance(result, ApplicationMaterials)
    assert result.email_subject == (
        "Application for AI Engineer Intern"
    )
    assert result.interview_focus == ["Python", "RAG"]


def test_generates_valid_learning_plan(monkeypatch):
    response = {
        "priority_steps": [
            {
                "skill": "LangChain",
                "reason": "It is required for the target role.",
                "actions": [
                    "Learn LangChain fundamentals",
                    "Build a small RAG application",
                ],
                "proof_project": "Create a PDF question-answering assistant.",
            }
        ],
        "suggested_project": "Build an evaluated RAG assistant.",
        "readiness_note": (
            "Apply after completing and documenting the project."
        ),
    }

    monkeypatch.setattr(
        action_generator,
        "create_gemini_model",
        lambda: FakeModel(response),
    )

    result = action_generator.generate_learning_plan(
        create_job_requirements(),
        create_match_analysis(),
        create_match_score(40),
    )

    assert isinstance(result, LearningPlan)
    assert len(result.priority_steps) == 1
    assert result.priority_steps[0].skill == "LangChain"