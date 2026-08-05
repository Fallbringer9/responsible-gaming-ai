from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PlayerActivitySnapshot:
    """Observed player activity over a defined analysis period."""

    player_id: str
    period_start: datetime
    period_end: datetime

    deposit_count: int
    total_deposit_amount: Decimal
    total_withdrawal_amount: Decimal
    total_wager_amount: Decimal
    total_win_amount: Decimal

    session_count: int
    nighttime_session_count: int
    limit_increase_request_count: int
    failed_deposit_attempt_count: int
    cancelled_withdrawal_count: int

    def __post_init__(self) -> None:
        normalized_player_id = self.player_id.strip()
        object.__setattr__(self, "player_id", normalized_player_id)

        self._validate_player_id()
        self._validate_period()
        self._validate_non_negative_values()

    def _validate_player_id(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must not be empty")

    def _validate_period(self) -> None:
        if self.period_end <= self.period_start:
            raise ValueError("period_end must be after period_start")

    def _validate_non_negative_values(self) -> None:
        numeric_values = {
            "deposit_count": self.deposit_count,
            "total_deposit_amount": self.total_deposit_amount,
            "total_withdrawal_amount": self.total_withdrawal_amount,
            "total_wager_amount": self.total_wager_amount,
            "total_win_amount": self.total_win_amount,
            "session_count": self.session_count,
            "nighttime_session_count": self.nighttime_session_count,
            "limit_increase_request_count": self.limit_increase_request_count,
            "failed_deposit_attempt_count": self.failed_deposit_attempt_count,
            "cancelled_withdrawal_count": self.cancelled_withdrawal_count,
        }

        for field_name, value in numeric_values.items():
            if value < 0:
                raise ValueError(f"{field_name} must not be negative")

        if self.nighttime_session_count > self.session_count:
            raise ValueError("nighttime_session_count must not exceed session_count")
