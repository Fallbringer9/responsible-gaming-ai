from enum import StrEnum


class RecommendationPriority(StrEnum):
    """Priority assigned to a recommendation."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
