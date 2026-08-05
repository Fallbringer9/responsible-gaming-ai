from datetime import UTC, datetime
from decimal import Decimal

from responsible_gaming.domain.cancelled_withdrawal_detector import (
    CancelledWithdrawalDetector,
)
from responsible_gaming.domain.failed_deposit_detector import FailedDepositDetector
from responsible_gaming.domain.frequent_deposit_detector import (
    FrequentDepositDetector,
)
from responsible_gaming.domain.high_deposit_detector import HighDepositDetector
from responsible_gaming.domain.limit_increase_detector import LimitIncreaseDetector
from responsible_gaming.domain.night_session_detector import NightSessionDetector
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService
from responsible_gaming.domain.risk_signal_code import RiskSignalCode


def build_snapshot(**overrides: object) -> PlayerActivitySnapshot:
    values = {
        "player_id": "player-123",
        "period_start": datetime(2026, 8, 1, tzinfo=UTC),
        "period_end": datetime(2026, 8, 2, tzinfo=UTC),
        "deposit_count": 5,
        "total_deposit_amount": Decimal("1500.00"),
        "total_withdrawal_amount": Decimal("200.00"),
        "total_wager_amount": Decimal("2000.00"),
        "total_win_amount": Decimal("1200.00"),
        "session_count": 8,
        "nighttime_session_count": 3,
        "limit_increase_request_count": 2,
        "failed_deposit_attempt_count": 4,
        "cancelled_withdrawal_count": 1,
    }

    values.update(overrides)

    return PlayerActivitySnapshot(**values)


def build_service() -> RiskAnalysisService:
    return RiskAnalysisService(
        detectors=(
            HighDepositDetector(threshold=Decimal("1000.00")),
            NightSessionDetector(threshold=2),
            FrequentDepositDetector(threshold=4),
            LimitIncreaseDetector(threshold=1),
            FailedDepositDetector(threshold=3),
            CancelledWithdrawalDetector(threshold=0),
        )
    )


def test_analyze_collects_all_detected_signals() -> None:
    service = build_service()
    snapshot = build_snapshot()

    result = service.analyze(snapshot)

    assert result.snapshot == snapshot
    assert tuple(signal.code for signal in result.signals) == (
        RiskSignalCode.HIGH_DEPOSIT,
        RiskSignalCode.NIGHT_SESSION,
        RiskSignalCode.FREQUENT_DEPOSIT,
        RiskSignalCode.LIMIT_INCREASE,
        RiskSignalCode.FAILED_DEPOSIT,
        RiskSignalCode.CANCELLED_WITHDRAWAL,
    )


def test_analyze_returns_empty_signals_when_no_rule_is_triggered() -> None:
    service = build_service()
    snapshot = build_snapshot(
        deposit_count=0,
        total_deposit_amount=Decimal("0"),
        session_count=0,
        nighttime_session_count=0,
        limit_increase_request_count=0,
        failed_deposit_attempt_count=0,
        cancelled_withdrawal_count=0,
    )

    result = service.analyze(snapshot)

    assert result.signals == ()
