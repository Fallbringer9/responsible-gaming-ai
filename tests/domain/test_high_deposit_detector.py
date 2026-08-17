from datetime import UTC, datetime
from decimal import Decimal

import pytest

from responsible_gaming.domain.high_deposit_detector import HighDepositDetector
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


def build_snapshot(**overrides: object) -> PlayerActivitySnapshot:
    values = {
        "player_id": "player-123",
        "period_start": datetime(2026, 7, 16, 8, 0, tzinfo=UTC),
        "period_end": datetime(2026, 7, 17, 8, 0, tzinfo=UTC),
        "deposit_count": 4,
        "total_deposit_amount": Decimal("250.00"),
        "total_withdrawal_amount": Decimal("200.00"),
        "total_wager_amount": Decimal("800.00"),
        "total_win_amount": Decimal("600.00"),
        "session_count": 3,
        "nighttime_session_count": 1,
        "limit_increase_request_count": 0,
        "failed_deposit_attempt_count": 1,
        "cancelled_withdrawal_count": 0,
    }

    values.update(overrides)

    return PlayerActivitySnapshot(**values)


def test_detect_returns_true_when_total_deposit_exceeds_threshold() -> None:
    detector = HighDepositDetector(threshold=Decimal("200"))

    snapshot = build_snapshot(
        total_deposit_amount=Decimal("250"),
    )

    signal = detector.detect(snapshot)

    assert signal is not None
    assert signal.code is RiskSignalCode.HIGH_DEPOSIT
    assert signal.severity is Severity.HIGH
    assert signal.observed_value == Decimal("250")
    assert signal.threshold == Decimal("200")


def test_detect_returns_false_when_total_deposit_equals_threshold() -> None:
    detector = HighDepositDetector(threshold=Decimal("250"))

    snapshot = build_snapshot(
        total_deposit_amount=Decimal("250"),
    )

    signal = detector.detect(snapshot)

    assert signal is None


def test_init_raises_when_threshold_is_negative() -> None:
    with pytest.raises(ValueError, match="threshold must not be negative"):
        HighDepositDetector(threshold=Decimal("-1"))
