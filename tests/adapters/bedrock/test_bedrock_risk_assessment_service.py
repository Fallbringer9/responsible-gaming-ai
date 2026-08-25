import json

import pytest

from responsible_gaming.adapters.bedrock.bedrock_risk_assessment_service import (
    BedrockRiskAssessmentService,
)
from responsible_gaming.application.ai.prompt import Prompt
from responsible_gaming.application.ai.recommendation_category import (
    RecommendationCategory,
)
from responsible_gaming.application.ai.recommendation_priority import (
    RecommendationPriority,
)
from responsible_gaming.application.ai.risk_level import RiskLevel


def valid_assessment_json() -> str:
    assessment = {
        "risk_level": "HIGH",
        "confidence": 0.91,
        "reasoning": (
            "Le joueur présente plusieurs signaux de pratique de jeu à risque."
        ),
        "recommendation": {
            "summary": "Une intervention de l'opérateur est recommandée.",
            "actions": [
                {
                    "title": "Contacter le joueur",
                    "description": (
                        "Contacter le joueur afin d'évaluer "
                        "sa situation et lui proposer des mesures adaptées."
                    ),
                    "priority": "HIGH",
                    "category": "HUMAN_CONTACT",
                }
            ],
        },
    }

    return json.dumps(assessment)


class FakeBedrockClient:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.converse_kwargs = None

    def converse(self, **kwargs):
        self.converse_kwargs = kwargs

        return {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": self.response_text,
                        }
                    ]
                }
            }
        }


def test_assess_maps_bedrock_response_to_risk_assessment() -> None:
    client = FakeBedrockClient(
        response_text=valid_assessment_json(),
    )

    service = BedrockRiskAssessmentService(
        client=client,
        model_id="test-model",
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse les signaux de risque de ce joueur.",
    )

    assessment = service.assess(prompt)

    assert assessment.risk_level is RiskLevel.HIGH
    assert assessment.confidence == 0.91
    assert (
        assessment.reasoning
        == "Le joueur présente plusieurs signaux de pratique de jeu à risque."
    )

    assert assessment.recommendation.summary == (
        "Une intervention de l'opérateur est recommandée."
    )

    assert len(assessment.recommendation.actions) == 1

    action = assessment.recommendation.actions[0]

    assert action.title == "Contacter le joueur"
    assert action.priority is RecommendationPriority.HIGH
    assert action.category is RecommendationCategory.HUMAN_CONTACT


def test_assess_accepts_json_wrapped_in_markdown_code_fence() -> None:
    response_text = f"""```json
{valid_assessment_json()}
```"""

    client = FakeBedrockClient(
        response_text=response_text,
    )

    service = BedrockRiskAssessmentService(
        client=client,
        model_id="test-model",
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse les signaux de risque de ce joueur.",
    )

    assessment = service.assess(prompt)

    assert assessment.risk_level is RiskLevel.HIGH
    assert assessment.confidence == 0.91


def test_assess_sends_prompt_and_model_id_to_bedrock() -> None:
    client = FakeBedrockClient(
        response_text=valid_assessment_json(),
    )

    service = BedrockRiskAssessmentService(
        client=client,
        model_id="test-model",
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse les signaux de risque de ce joueur.",
    )

    service.assess(prompt)

    assert client.converse_kwargs == {
        "modelId": "test-model",
        "system": [
            {
                "text": "Tu es un expert en jeu responsable.",
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "Analyse les signaux de risque de ce joueur.",
                    }
                ],
            }
        ],
    }


def test_assess_raises_error_when_bedrock_returns_invalid_json() -> None:
    client = FakeBedrockClient(
        response_text="Le joueur présente un risque élevé.",
    )

    service = BedrockRiskAssessmentService(
        client=client,
        model_id="test-model",
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse les signaux de risque de ce joueur.",
    )

    with pytest.raises(json.JSONDecodeError):
        service.assess(prompt)


def test_assess_raises_error_when_risk_level_is_invalid() -> None:
    assessment = json.loads(valid_assessment_json())
    assessment["risk_level"] = "SUPER_HIGH"

    client = FakeBedrockClient(
        response_text=json.dumps(assessment),
    )

    service = BedrockRiskAssessmentService(
        client=client,
        model_id="test-model",
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse les signaux de risque de ce joueur.",
    )

    with pytest.raises(ValueError):
        service.assess(prompt)
