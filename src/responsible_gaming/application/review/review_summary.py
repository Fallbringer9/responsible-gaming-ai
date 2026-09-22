from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    assessment: dict[str, Any]
    review_status: str
