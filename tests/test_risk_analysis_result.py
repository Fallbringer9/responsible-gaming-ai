from datetime import UTC, datetime
from decimal import Decimal

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


def test_result_contains_snapshot_and_detected_signals() -> None:
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

    signal = RiskSignal(
        code=RiskSignalCode.HIGH_DEPOSIT,
        severity=Severity.HIGH,
        observed_value=Decimal("1500"),
        threshold=Decimal("1000"),
    )

    result = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(signal,),
    )

    assert result.snapshot is snapshot
    assert result.signals == (signal,)
