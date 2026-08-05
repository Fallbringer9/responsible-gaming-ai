from dataclasses import dataclass

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_signal import RiskSignal


@dataclass(frozen=True, slots=True)
class RiskAnalysisResult:
    """Deterministic risk signals detected for one player activity period."""

    snapshot: PlayerActivitySnapshot
    signals: tuple[RiskSignal, ...]
