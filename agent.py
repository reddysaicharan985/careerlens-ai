from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from services.action_generator import (
    generate_application_materials,
    generate_learning_plan,
)
from services.action_schema import (
    ApplicationMaterials,
    LearningPlan,
)
from services.job_parser import parse_job_description
from services.job_schema import JobRequirements
from services.match_schema import ResumeMatchAnalysis
from services.resume_matcher import match_resume_to_job
from services.scoring import MatchScore, calculate_match_score


class CareerLensState(TypedDict, total=False):
    """Shared state passed between CareerLens agent nodes."""

    safe_resume_text: str
    job_description: str

    job_requirements: JobRequirements
    match_analysis: ResumeMatchAnalysis
    match_score: MatchScore

    application_materials: ApplicationMaterials
    learning_plan: LearningPlan

    error: str


def parse_job_node(state):
    """Convert the job description into validated requirements."""

    job_requirements = parse_job_description(
        state["job_description"]
    )

    return {
        "job_requirements": job_requirements,
    }


def match_resume_node(state):
    """Compare protected resume evidence with the job."""

    match_analysis = match_resume_to_job(
        state["safe_resume_text"],
        state["job_requirements"],
    )

    return {
        "match_analysis": match_analysis,
    }


def score_match_node(state):
    """Calculate the deterministic match score."""

    match_score = calculate_match_score(
        state["job_requirements"],
        state["match_analysis"],
    )

    return {
        "match_score": match_score,
    }


def route_after_scoring(
    state,
) -> Literal[
    "prepare_application",
    "create_learning_plan",
]:
    """Choose the next agent node using the match score."""

    match_score = state.get("match_score")

    if match_score is None:
        raise ValueError(
            "The agent cannot route without a match score."
        )

    if match_score.overall_score >= 50:
        return "prepare_application"

    return "create_learning_plan"


def prepare_application_node(state):
    """Generate truthful application materials."""

    application_materials = generate_application_materials(
        state["safe_resume_text"],
        state["job_requirements"],
        state["match_analysis"],
        state["match_score"],
    )

    return {
        "application_materials": application_materials,
    }


def create_learning_plan_node(state):
    """Generate a targeted skill-development plan."""

    learning_plan = generate_learning_plan(
        state["job_requirements"],
        state["match_analysis"],
        state["match_score"],
    )

    return {
        "learning_plan": learning_plan,
    }


def build_careerlens_agent():
    """Build and compile the CareerLens LangGraph workflow."""

    graph = StateGraph(CareerLensState)

    graph.add_node("parse_job", parse_job_node)
    graph.add_node("match_resume", match_resume_node)
    graph.add_node("score_match", score_match_node)
    graph.add_node(
        "prepare_application",
        prepare_application_node,
    )
    graph.add_node(
        "create_learning_plan",
        create_learning_plan_node,
    )

    graph.add_edge(START, "parse_job")
    graph.add_edge("parse_job", "match_resume")
    graph.add_edge("match_resume", "score_match")

    graph.add_conditional_edges(
        "score_match",
        route_after_scoring,
        {
            "prepare_application": "prepare_application",
            "create_learning_plan": "create_learning_plan",
        },
    )

    graph.add_edge("prepare_application", END)
    graph.add_edge("create_learning_plan", END)

    return graph.compile()


careerlens_agent = build_careerlens_agent()