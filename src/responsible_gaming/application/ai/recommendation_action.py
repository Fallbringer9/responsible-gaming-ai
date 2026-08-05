from dataclasses import dataclass

from responsible_gaming.application.ai.recommendation_category import (
    RecommendationCategory,
)
from responsible_gaming.application.ai.recommendation_priority import (
    RecommendationPriority,
)


@dataclass(frozen=True, slots=True)
class RecommendationAction:
    """Single action recommended by the AI."""

    title: str
    description: str
    priority: RecommendationPriority
    category: RecommendationCategory

    def __post_init__(self) -> None:
        normalized_title = self.title.strip()
        normalized_description = self.description.strip()

        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "description", normalized_description)

        if not self.title:
            raise ValueError("title must not be empty")

        if not self.description:
            raise ValueError("description must not be empty")
