from datetime import UTC, datetime
from decimal import Decimal

import pytest

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot


def build_snapshot(**overrides: object) -> PlayerActivitySnapshot:
    values = {
        "player_id": "player-123",
        "period_start": datetime(2026, 7, 16, 8, 0, tzinfo=UTC),
        "period_end": datetime(2026, 7, 17, 8, 0, tzinfo=UTC),
        "deposit_count": 4,
        "total_deposit_amount": Decimal("250.00"),
        "total_withdrawal_amount": Decimal("200"),
        "total_wager_amount": Decimal("800"),
        "total_win_amount": Decimal("600"),
        "cancelled_withdrawal_count": 0,
        "session_count": 3,
        "nighttime_session_count": 1,
        "limit_increase_request_count": 0,
        "failed_deposit_attempt_count": 1,
    }

    values.update(overrides)

    return PlayerActivitySnapshot(**values)


def test_create_valid_snapshot() -> None:
    snapshot = build_snapshot()

    assert snapshot.player_id == "player-123"
    assert snapshot.total_deposit_amount == Decimal("250.00")


def test_player_id_is_trimmed() -> None:
    snapshot = build_snapshot(player_id="  player-123  ")

    assert snapshot.player_id == "player-123"


def test_empty_player_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="player_id must not be empty"):
        build_snapshot(player_id="   ")


def test_period_end_must_be_after_period_start() -> None:
    start = datetime(2026, 7, 16, 8, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="period_end must be after period_start",
    ):
        build_snapshot(
            period_start=start,
            period_end=start,
        )


def test_negative_values_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="deposit_count must not be negative",
    ):
        build_snapshot(deposit_count=-1)


def test_nighttime_sessions_cannot_exceed_total_sessions() -> None:
    with pytest.raises(
        ValueError,
        match="nighttime_session_count must not exceed session_count",
    ):
        build_snapshot(
            session_count=1,
            nighttime_session_count=2,
        )
