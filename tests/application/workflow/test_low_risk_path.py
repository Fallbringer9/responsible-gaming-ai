from responsible_gaming.application.workflow.nodes import (
    build_low_risk_assessment_node,
    route_after_analysis,
)
from responsible_gaming.application.workflow.state import ResponsibleGamingState


def _build_state_with_signals(
    signals: list[dict],
) -> ResponsibleGamingState:
    return {
        "snapshot": {
            "player_id": "TEST-PLAYER",
            "period_start": "2026-09-16T00:00:00+00:00",
            "period_end": "2026-09-23T00:00:00+00:00",
            "deposit_count": 1,
            "total_deposit_amount": "100",
            "total_withdrawal_amount": "50",
            "total_wager_amount": "100",
            "total_win_amount": "80",
            "session_count": 2,
            "nighttime_session_count": 0,
            "limit_increase_request_count": 0,
            "failed_deposit_attempt_count": 0,
            "cancelled_withdrawal_count": 0,
        },
        "analysis": {
            "snapshot": {
                "player_id": "TEST-PLAYER",
                "period_start": "2026-09-16T00:00:00+00:00",
                "period_end": "2026-09-23T00:00:00+00:00",
                "deposit_count": 1,
                "total_deposit_amount": "100",
                "total_withdrawal_amount": "50",
                "total_wager_amount": "100",
                "total_win_amount": "80",
                "session_count": 2,
                "nighttime_session_count": 0,
                "limit_increase_request_count": 0,
                "failed_deposit_attempt_count": 0,
                "cancelled_withdrawal_count": 0,
            },
            "signals": signals,
        },
    }


def test_route_to_low_risk_when_no_signal_exists() -> None:
    state = _build_state_with_signals([])

    result = route_after_analysis(state)

    assert result == "build_low_risk_assessment"


def test_route_to_knowledge_retrieval_when_signal_exists() -> None:
    state = _build_state_with_signals(
        [
            {
                "code": "HIGH_DEPOSIT",
                "severity": "HIGH",
                "observed_value": "1500",
                "threshold": "1000",
            }
        ]
    )

    result = route_after_analysis(state)

    assert result == "retrieve_knowledge"


def test_low_risk_assessment_does_not_require_human_review() -> None:
    state = _build_state_with_signals([])

    result = build_low_risk_assessment_node(state)

    assert result["assessment"]["risk_level"] == "LOW"
    assert result["assessment"]["confidence"] == 1.0
    assert result["human_review_required"] is False
