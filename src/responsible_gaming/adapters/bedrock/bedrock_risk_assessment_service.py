import json
from typing import Any

from responsible_gaming.application.ai.prompt import Prompt
from responsible_gaming.application.ai.recommendation import Recommendation
from responsible_gaming.application.ai.recommendation_action import (
    RecommendationAction,
)
from responsible_gaming.application.ai.recommendation_category import (
    RecommendationCategory,
)
from responsible_gaming.application.ai.recommendation_priority import (
    RecommendationPriority,
)
from responsible_gaming.application.ai.risk_assessment import RiskAssessment
from responsible_gaming.application.ai.risk_assessment_service import (
    RiskAssessmentService,
)
from responsible_gaming.application.ai.risk_level import RiskLevel


def _parse_json_response(response_text: str) -> dict[str, Any]:
    normalized = response_text.strip()

    if normalized.startswith("```json") and normalized.endswith("```"):
        normalized = normalized.removeprefix("```json")
        normalized = normalized.removesuffix("```")
        normalized = normalized.strip()

    return json.loads(normalized)


class BedrockRiskAssessmentService(RiskAssessmentService):
    """Produces risk assessments using Amazon Bedrock."""

    def __init__(
        self,
        client: Any,
        model_id: str,
    ) -> None:
        self._client = client
        self._model_id = model_id

    def assess(
        self,
        prompt: Prompt,
    ) -> RiskAssessment:
        response = self._client.converse(
            modelId=self._model_id,
            system=[
                {
                    "text": prompt.system_prompt,
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt.user_prompt,
                        }
                    ],
                }
            ],
        )

        response_text = response["output"]["message"]["content"][0]["text"]

        data = _parse_json_response(response_text)

        recommendation_data = data["recommendation"]

        actions = []

        for action_data in recommendation_data["actions"]:
            action = RecommendationAction(
                title=action_data["title"],
                description=action_data["description"],
                priority=RecommendationPriority(
                    action_data["priority"],
                ),
                category=RecommendationCategory(
                    action_data["category"],
                ),
            )

            actions.append(action)

        recommendation = Recommendation(
            summary=recommendation_data["summary"],
            actions=tuple(actions),
        )

        return RiskAssessment(
            risk_level=RiskLevel(data["risk_level"]),
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            recommendation=recommendation,
        )
