from dataclasses import dataclass

from responsible_gaming.application.ai.recommendation import Recommendation
from responsible_gaming.application.ai.risk_level import RiskLevel


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    """Structured assessment produced by the AI."""

    risk_level: RiskLevel
    confidence: float
    reasoning: str
    recommendation: Recommendation

    def __post_init__(self) -> None:
        normalized_reasoning = self.reasoning.strip()
        object.__setattr__(self, "reasoning", normalized_reasoning)

        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

        if not self.reasoning:
            raise ValueError("reasoning must not be empty")
