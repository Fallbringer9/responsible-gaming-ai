import pytest

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


def test_create_valid_recommendation_action() -> None:
    action = build_action()

    assert action.title == "Suggest a deposit limit"
    assert action.description == (
        "Invite the player to configure a voluntary deposit limit."
    )
    assert action.priority is RecommendationPriority.HIGH
    assert action.category is RecommendationCategory.DEPOSIT_LIMIT


def test_trim_title_and_description() -> None:
    action = build_action(
        title="  Suggest a deposit limit  ",
        description="  Invite the player to configure a limit.  ",
    )

    assert action.title == "Suggest a deposit limit"
    assert action.description == ("Invite the player to configure a limit.")


def test_raise_when_title_is_empty() -> None:
    with pytest.raises(ValueError, match="title must not be empty"):
        build_action(title="   ")


def test_raise_when_description_is_empty() -> None:
    with pytest.raises(ValueError, match="description must not be empty"):
        build_action(description="")
