from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ReviewDecisionType(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: ReviewDecisionType
    comment: str | None = None
