from dataclasses import dataclass

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


@dataclass(frozen=True, slots=True)
class FailedDepositDetector:
    threshold: int

    def __post_init__(self) -> None:
        if self.threshold < 0:
            raise ValueError("threshold must not be negative")

    def detect(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskSignal | None:
        if snapshot.failed_deposit_attempt_count <= self.threshold:
            return None

        return RiskSignal(
            code=RiskSignalCode.FAILED_DEPOSIT,
            severity=Severity.MEDIUM,
            observed_value=snapshot.failed_deposit_attempt_count,
            threshold=self.threshold,
        )
