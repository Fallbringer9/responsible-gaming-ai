from datetime import UTC, datetime
from decimal import Decimal

from responsible_gaming.application.rag.default_knowledge_query_builder import (
    DefaultKnowledgeQueryBuilder,
)
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


def test_build_returns_knowledge_query_from_risk_analysis() -> None:
    builder = DefaultKnowledgeQueryBuilder()

    snapshot = PlayerActivitySnapshot(
        player_id="player-123",
        period_start=datetime(2026, 8, 1, tzinfo=UTC),
        period_end=datetime(2026, 8, 2, tzinfo=UTC),
        deposit_count=0,
        total_deposit_amount=Decimal("0"),
        total_withdrawal_amount=Decimal("0"),
        total_wager_amount=Decimal("0"),
        total_win_amount=Decimal("0"),
        session_count=0,
        nighttime_session_count=0,
        limit_increase_request_count=0,
        failed_deposit_attempt_count=0,
        cancelled_withdrawal_count=0,
    )

    analysis = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(
            RiskSignal(
                code=RiskSignalCode.FAILED_DEPOSIT,
                severity=Severity.HIGH,
                observed_value=5,
                threshold=3,
            ),
            RiskSignal(
                code=RiskSignalCode.NIGHT_SESSION,
                severity=Severity.MEDIUM,
                observed_value=8,
                threshold=5,
            ),
        ),
    )

    query = builder.build(analysis)

    assert "Tentatives de dépôt refusées" in query.text
    assert "Sessions de jeu nocturnes" in query.text
