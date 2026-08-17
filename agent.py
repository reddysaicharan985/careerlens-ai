from typing import Literal, TypedDict

from services.job_schema import JobRequirements
from services.match_schema import ResumeMatchAnalysis
from services.scoring import MatchScore


class CareerLensState(TypedDict, total=False):
    """Shared state passed between CareerLens agent nodes."""

    resume_text: str
    safe_resume_text: str
    job_description: str

    page_count: int
    redaction_counts: dict[str, int]

    job_requirements: JobRequirements
    match_analysis: ResumeMatchAnalysis
    match_score: MatchScore

    next_route: Literal[
        "prepare_application",
        "create_learning_plan",
    ]

    application_email: str
    cover_letter: str
    learning_plan: list[str]

    error: str


def route_after_scoring(state):
    """Choose the next agent step using the match score."""

    match_score = state.get("match_score")

    if match_score is None:
        raise ValueError(
            "The agent cannot route without a match score."
        )

    if match_score.overall_score >= 50:
        return "prepare_application"

    return "create_learning_plan"