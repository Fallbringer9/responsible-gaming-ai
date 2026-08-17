from typing import Protocol

from responsible_gaming.application.ai.prompt import Prompt
from responsible_gaming.application.ai.risk_assessment import RiskAssessment


class RiskAssessmentService(Protocol):
    """Produces a structured risk assessment from an AI prompt."""

    def assess(
        self,
        prompt: Prompt,
    ) -> RiskAssessment: ...
