from dataclasses import dataclass
from decimal import Decimal

from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


@dataclass(frozen=True, slots=True)
class RiskSignal:
    code: RiskSignalCode
    severity: Severity
    observed_value: Decimal | int
    threshold: Decimal | int

    @property
    def title(self) -> str:
        return _SIGNAL_METADATA[self.code]["title"]

    @property
    def description(self) -> str:
        return _SIGNAL_METADATA[self.code]["description"]


_SIGNAL_METADATA = {
    RiskSignalCode.HIGH_DEPOSIT: {
        "title": "High deposit amount",
        "description": (
            "The player's total deposits exceeded the configured threshold."
        ),
    },
    RiskSignalCode.NIGHT_SESSION: {
        "title": "Night sessions",
        "description": ("The player exceeded the configured number of night sessions."),
    },
    RiskSignalCode.FREQUENT_DEPOSIT: {
        "title": "Frequent deposits",
        "description": ("The player exceeded the configured number of deposits."),
    },
    RiskSignalCode.LIMIT_INCREASE: {
        "title": "Limit increase requests",
        "description": (
            "The player exceeded the configured number of limit increase requests."
        ),
    },
    RiskSignalCode.FAILED_DEPOSIT: {
        "title": "Failed deposit attempts",
        "description": (
            "The player exceeded the configured number of failed deposit attempts."
        ),
    },
    RiskSignalCode.CANCELLED_WITHDRAWAL: {
        "title": "Cancelled withdrawals",
        "description": (
            "The player exceeded the configured number of cancelled withdrawals."
        ),
    },
}
