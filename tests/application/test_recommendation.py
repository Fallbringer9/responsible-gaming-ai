import pytest

from responsible_gaming.application.ai.recommendation import Recommendation
from responsible_gaming.application.ai.recommendation_action import (
    RecommendationAction,
)
from responsible_gaming.application.ai.recommendation_category import (
    RecommendationCategory,
)
from responsible_gaming.application.ai.recommendation_priority import (
    RecommendationPriority,
)


def build_action(**overrides: object) -> RecommendationAction:
    values = {
        "title": "Suggest a deposit limit",
        "description": ("Invite the player to configure a voluntary deposit limit."),
        "priority": RecommendationPriority.HIGH,
        "category": RecommendationCategory.DEPOSIT_LIMIT,
    }

    values.update(overrides)

    return RecommendationAction(**values)


def build_recommendation(**overrides: object) -> Recommendation:
    values = {
        "summary": (
            "The player demonstrates several responsible gaming risk indicators."
        ),
        "actions": (build_action(),),
    }

    values.update(overrides)

    return Recommendation(**values)


def test_create_valid_recommendation() -> None:
    recommendation = build_recommendation()

    assert recommendation.summary == (
        "The player demonstrates several responsible gaming risk indicators."
    )

    assert len(recommendation.actions) == 1


def test_summary_is_trimmed() -> None:
    recommendation = build_recommendation(
        summary="   Player should be contacted.   ",
    )

    assert recommendation.summary == "Player should be contacted."


def test_raise_when_summary_is_empty() -> None:
    with pytest.raises(
        ValueError,
        match="summary must not be empty",
    ):
        build_recommendation(summary="    ")


def test_raise_when_actions_are_empty() -> None:
    with pytest.raises(
        ValueError,
        match="recommendation must contain at least one action",
    ):
        build_recommendation(actions=())
