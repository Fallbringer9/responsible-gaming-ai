from enum import StrEnum


class RiskLevel(StrEnum):
    """Risk level assigned by the AI assessment."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
