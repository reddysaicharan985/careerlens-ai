import pytest

from agent import route_after_scoring
from services.scoring import MatchScore


def create_score(overall_score):
    return MatchScore(
        overall_score=overall_score,
        recommendation="Test recommendation",
        required_skill_score=None,
        preferred_skill_score=None,
        education_score=None,
        experience_score=None,
    )


def test_strong_match_routes_to_application():
    state = {
        "match_score": create_score(88),
    }

    assert route_after_scoring(state) == (
        "prepare_application"
    )


def test_boundary_score_routes_to_application():
    state = {
        "match_score": create_score(50),
    }

    assert route_after_scoring(state) == (
        "prepare_application"
    )


def test_low_match_routes_to_learning_plan():
    state = {
        "match_score": create_score(49),
    }

    assert route_after_scoring(state) == (
        "create_learning_plan"
    )


def test_missing_score_stops_the_agent():
    with pytest.raises(
        ValueError,
        match="cannot route without a match score",
    ):
        route_after_scoring({})