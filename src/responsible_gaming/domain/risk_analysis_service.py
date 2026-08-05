from dataclasses import dataclass

from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult
from responsible_gaming.domain.signal_detector import SignalDetector


@dataclass(frozen=True, slots=True)
class RiskAnalysisService:
    """Run deterministic signal detectors against player activity."""

    detectors: tuple[SignalDetector, ...]

    def analyze(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskAnalysisResult:
        signals = tuple(
            signal
            for detector in self.detectors
            if (signal := detector.detect(snapshot)) is not None
        )

        return RiskAnalysisResult(
            snapshot=snapshot,
            signals=signals,
        )
