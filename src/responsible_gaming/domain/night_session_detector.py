from dataclasses import dataclass

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


@dataclass(frozen=True, slots=True)
class NightSessionDetector:
    threshold: int

    def __post_init__(self) -> None:
        if self.threshold < 0:
            raise ValueError("threshold must not be negative")

    def detect(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskSignal | None:
        if snapshot.nighttime_session_count <= self.threshold:
            return None

        return RiskSignal(
            code=RiskSignalCode.NIGHT_SESSION,
            severity=Severity.MEDIUM,
            observed_value=snapshot.nighttime_session_count,
            threshold=self.threshold,
        )
