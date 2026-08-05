from typing import Protocol

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_signal import RiskSignal


class SignalDetector(Protocol):
    """Contract implemented by deterministic risk signal detectors."""

    def detect(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskSignal | None:
        """Return a detected signal or None when the rule is not triggered."""
        ...
