from dataclasses import dataclass
from decimal import Decimal

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


@dataclass(frozen=True, slots=True)
class HighDepositDetector:
    threshold: Decimal

    def __post_init__(self) -> None:
        if self.threshold < 0:
            raise ValueError("threshold must not be negative")

    def detect(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskSignal | None:
        if snapshot.total_deposit_amount <= self.threshold:
            return None

        return RiskSignal(
            code=RiskSignalCode.HIGH_DEPOSIT,
            severity=Severity.HIGH,
            observed_value=snapshot.total_deposit_amount,
            threshold=self.threshold,
        )
