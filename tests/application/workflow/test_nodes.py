from datetime import UTC, datetime
from decimal import Decimal

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
from responsible_gaming.application.workflow.nodes import (
    analyze_node,
    decide_human_review_node,
)
from responsible_gaming.application.workflow.state_mapper import (
    analysis_from_state,
    assessment_to_state,
    snapshot_to_state,
)
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult


class FakeRiskAnalysisService:
    def __init__(
        self,
        result: RiskAnalysisResult,
    ) -> None:
        self.result = result
        self.received_snapshot = None

    def analyze(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskAnalysisResult:
        self.received_snapshot = snapshot
        return self.result


def build_assessment(
    risk_level: RiskLevel,
) -> RiskAssessment:
    action = RecommendationAction(
        title="Test action",
        description="Test action description.",
        priority=RecommendationPriority.MEDIUM,
        category=RecommendationCategory.RESPONSIBLE_GAMING_INFORMATION,
    )

    recommendation = Recommendation(
        summary="Test recommendation.",
        actions=(action,),
    )

    return RiskAssessment(
        risk_level=risk_level,
        confidence=0.90,
        reasoning="Test reasoning.",
        recommendation=recommendation,
    )


def test_analyze_node_calls_service_and_returns_analysis() -> None:
    snapshot = PlayerActivitySnapshot(
        player_id="player-123",
        period_start=datetime(2026, 8, 1, tzinfo=UTC),
        period_end=datetime(2026, 8, 2, tzinfo=UTC),
        deposit_count=5,
        total_deposit_amount=Decimal("500"),
        total_withdrawal_amount=Decimal("100"),
        total_wager_amount=Decimal("600"),
        total_win_amount=Decimal("200"),
        session_count=4,
        nighttime_session_count=1,
        limit_increase_request_count=0,
        failed_deposit_attempt_count=0,
        cancelled_withdrawal_count=0,
    )

    expected_analysis = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(),
    )

    service = FakeRiskAnalysisService(
        result=expected_analysis,
    )

    state = {
        "snapshot": snapshot_to_state(snapshot),
    }

    result = analyze_node(
        state=state,
        analysis_service=service,
    )

    analysis = analysis_from_state(
        result["analysis"],
    )

    assert service.received_snapshot == snapshot
    assert analysis == expected_analysis


def test_decide_human_review_requires_review_for_high_risk() -> None:
    assessment = build_assessment(
        RiskLevel.HIGH,
    )

    state = {
        "assessment": assessment_to_state(
            assessment,
        ),
    }

    result = decide_human_review_node(
        state,
    )

    assert result == {
        "human_review_required": True,
    }


def test_decide_human_review_requires_review_for_critical_risk() -> None:
    assessment = build_assessment(
        RiskLevel.CRITICAL,
    )

    state = {
        "assessment": assessment_to_state(
            assessment,
        ),
    }

    result = decide_human_review_node(
        state,
    )

    assert result == {
        "human_review_required": True,
    }


def test_decide_human_review_does_not_require_review_for_low_risk() -> None:
    assessment = build_assessment(
        RiskLevel.LOW,
    )

    state = {
        "assessment": assessment_to_state(
            assessment,
        ),
    }

    result = decide_human_review_node(
        state,
    )

    assert result == {
        "human_review_required": False,
    }


def test_decide_human_review_does_not_require_review_for_medium_risk() -> None:
    assessment = build_assessment(
        RiskLevel.MEDIUM,
    )

    state = {
        "assessment": assessment_to_state(
            assessment,
        ),
    }

    result = decide_human_review_node(
        state,
    )

    assert result == {
        "human_review_required": False,
    }
