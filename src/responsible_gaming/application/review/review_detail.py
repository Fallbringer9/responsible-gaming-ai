from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    assessment: dict[str, Any]
    human_review_required: bool
    review_status: str | None = None
    review_comment: str | None = None
