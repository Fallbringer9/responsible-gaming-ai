from enum import StrEnum


class RecommendationCategory(StrEnum):
    """Categories of responsible gaming recommendations."""

    DEPOSIT_LIMIT = "DEPOSIT_LIMIT"
    LOSS_LIMIT = "LOSS_LIMIT"
    SESSION_LIMIT = "SESSION_LIMIT"
    COOLING_OFF = "COOLING_OFF"
    SELF_EXCLUSION = "SELF_EXCLUSION"
    RESPONSIBLE_GAMING_INFORMATION = "RESPONSIBLE_GAMING_INFORMATION"
    HUMAN_CONTACT = "HUMAN_CONTACT"
