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
from responsible_gaming.application.ai.risk_assessment import RiskAssessment
from responsible_gaming.application.ai.risk_level import RiskLevel


def build_action() -> RecommendationAction:
    return RecommendationAction(
        title="Suggest a deposit limit",
        description="Invite the player to configure a voluntary deposit limit.",
        priority=RecommendationPriority.HIGH,
        category=RecommendationCategory.DEPOSIT_LIMIT,
    )


def build_recommendation() -> Recommendation:
    return Recommendation(
        summary="The player should receive tailored responsible gaming support.",
        actions=(build_action(),),
    )


def build_assessment(**overrides: object) -> RiskAssessment:
    values = {
        "risk_level": RiskLevel.HIGH,
        "confidence": 0.92,
        "reasoning": (
            "The player presents multiple financial and behavioural risk signals."
        ),
        "recommendation": build_recommendation(),
    }

    values.update(overrides)

    return RiskAssessment(**values)


def test_create_valid_risk_assessment() -> None:
    assessment = build_assessment()

    assert assessment.risk_level is RiskLevel.HIGH
    assert assessment.confidence == 0.92
    assert assessment.recommendation.actions


def test_reasoning_is_trimmed() -> None:
    assessment = build_assessment(
        reasoning="  Multiple risk signals were detected.  ",
    )

    assert assessment.reasoning == "Multiple risk signals were detected."


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_confidence_outside_valid_range_is_rejected(confidence: float) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 1",
    ):
        build_assessment(confidence=confidence)


def test_empty_reasoning_is_rejected() -> None:
    with pytest.raises(ValueError, match="reasoning must not be empty"):
        build_assessment(reasoning="   ")
