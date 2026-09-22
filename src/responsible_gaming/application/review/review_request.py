from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    assessment: dict[str, Any]
    task_token: str
