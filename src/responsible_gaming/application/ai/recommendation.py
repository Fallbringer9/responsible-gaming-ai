from dataclasses import dataclass

from responsible_gaming.application.ai.recommendation_action import (
    RecommendationAction,
)


@dataclass(frozen=True, slots=True)
class Recommendation:
    """Collection of actions recommended by the AI."""

    summary: str
    actions: tuple[RecommendationAction, ...]

    def __post_init__(self) -> None:
        normalized_summary = self.summary.strip()

        object.__setattr__(self, "summary", normalized_summary)

        if not self.summary:
            raise ValueError("summary must not be empty")

        if not self.actions:
            raise ValueError("recommendation must contain at least one action")
