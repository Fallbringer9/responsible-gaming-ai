from decimal import Decimal
from typing import Any

import responsible_gaming.bootstrap.composition_root as composition_root
from responsible_gaming.adapters.bedrock.bedrock_knowledge_retriever import (
    BedrockKnowledgeRetriever,
)
from responsible_gaming.adapters.bedrock.bedrock_risk_assessment_service import (
    BedrockRiskAssessmentService,
)
from responsible_gaming.application.ai.default_prompt_builder import (
    DefaultPromptBuilder,
)
from responsible_gaming.application.rag.default_knowledge_query_builder import (
    DefaultKnowledgeQueryBuilder,
)
from responsible_gaming.application.use_cases.analyze_player_use_case import (
    AnalyzePlayerUseCase,
)
from responsible_gaming.bootstrap.composition_root import RiskThresholds
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService


class FakeBedrockClientFactory:
    def __init__(self, region_name: str) -> None:
        self.region_name = region_name

    def create_knowledge_base_client(self) -> Any:
        return object()

    def create_runtime_client(self) -> Any:
        return object()


def test_build_analyze_player_use_case_wires_dependencies(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        composition_root,
        "BedrockClientFactory",
        FakeBedrockClientFactory,
    )

    thresholds = RiskThresholds(
        high_deposit=Decimal("1000"),
        frequent_deposit=5,
        night_session=3,
        limit_increase=1,
        failed_deposit=3,
        cancelled_withdrawal=2,
    )

    use_case = composition_root.build_analyze_player_use_case(
        region_name="eu-west-3",
        knowledge_base_id="kb-test",
        model_id="model-test",
        thresholds=thresholds,
    )

    assert isinstance(use_case, AnalyzePlayerUseCase)

    assert isinstance(
        use_case.risk_analysis_service,
        RiskAnalysisService,
    )
    assert len(use_case.risk_analysis_service.detectors) == 6

    assert isinstance(
        use_case.knowledge_query_builder,
        DefaultKnowledgeQueryBuilder,
    )
    assert isinstance(
        use_case.knowledge_retriever,
        BedrockKnowledgeRetriever,
    )
    assert isinstance(
        use_case.prompt_builder,
        DefaultPromptBuilder,
    )
    assert isinstance(
        use_case.risk_assessment_service,
        BedrockRiskAssessmentService,
    )
