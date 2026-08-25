from dataclasses import dataclass
from decimal import Decimal

from responsible_gaming.adapters.bedrock.bedrock_client_factory import (
    BedrockClientFactory,
)
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
from responsible_gaming.application.workflow.graph import (
    build_responsible_gaming_graph,
)
from responsible_gaming.domain.cancelled_withdrawal_detector import (
    CancelledWithdrawalDetector,
)
from responsible_gaming.domain.failed_deposit_detector import (
    FailedDepositDetector,
)
from responsible_gaming.domain.frequent_deposit_detector import (
    FrequentDepositDetector,
)
from responsible_gaming.domain.high_deposit_detector import (
    HighDepositDetector,
)
from responsible_gaming.domain.limit_increase_detector import (
    LimitIncreaseDetector,
)
from responsible_gaming.domain.night_session_detector import (
    NightSessionDetector,
)
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService


@dataclass(frozen=True, slots=True)
class RiskThresholds:
    high_deposit: Decimal
    frequent_deposit: int
    night_session: int
    limit_increase: int
    failed_deposit: int
    cancelled_withdrawal: int


def _build_dependencies(
    *,
    region_name: str,
    knowledge_base_id: str,
    model_id: str,
    thresholds: RiskThresholds,
    profile_name: str | None = None,
):
    client_factory = BedrockClientFactory(
        region_name=region_name,
        profile_name=profile_name,
    )

    risk_analysis_service = RiskAnalysisService(
        detectors=(
            HighDepositDetector(
                threshold=thresholds.high_deposit,
            ),
            FrequentDepositDetector(
                threshold=thresholds.frequent_deposit,
            ),
            NightSessionDetector(
                threshold=thresholds.night_session,
            ),
            LimitIncreaseDetector(
                threshold=thresholds.limit_increase,
            ),
            FailedDepositDetector(
                threshold=thresholds.failed_deposit,
            ),
            CancelledWithdrawalDetector(
                threshold=thresholds.cancelled_withdrawal,
            ),
        ),
    )

    knowledge_query_builder = DefaultKnowledgeQueryBuilder()

    knowledge_retriever = BedrockKnowledgeRetriever(
        client=client_factory.create_knowledge_base_client(),
        knowledge_base_id=knowledge_base_id,
    )

    prompt_builder = DefaultPromptBuilder()

    risk_assessment_service = BedrockRiskAssessmentService(
        client=client_factory.create_runtime_client(),
        model_id=model_id,
    )

    return (
        risk_analysis_service,
        knowledge_query_builder,
        knowledge_retriever,
        prompt_builder,
        risk_assessment_service,
    )


def build_analyze_player_use_case(
    *,
    region_name: str,
    knowledge_base_id: str,
    model_id: str,
    thresholds: RiskThresholds,
    profile_name: str | None = None,
) -> AnalyzePlayerUseCase:
    (
        risk_analysis_service,
        knowledge_query_builder,
        knowledge_retriever,
        prompt_builder,
        risk_assessment_service,
    ) = _build_dependencies(
        region_name=region_name,
        knowledge_base_id=knowledge_base_id,
        model_id=model_id,
        thresholds=thresholds,
        profile_name=profile_name,
    )

    return AnalyzePlayerUseCase(
        risk_analysis_service=risk_analysis_service,
        knowledge_query_builder=knowledge_query_builder,
        knowledge_retriever=knowledge_retriever,
        prompt_builder=prompt_builder,
        risk_assessment_service=risk_assessment_service,
    )


def build_responsible_gaming_workflow(
    *,
    region_name: str,
    knowledge_base_id: str,
    model_id: str,
    thresholds: RiskThresholds,
    profile_name: str | None = None,
):
    (
        risk_analysis_service,
        knowledge_query_builder,
        knowledge_retriever,
        prompt_builder,
        risk_assessment_service,
    ) = _build_dependencies(
        region_name=region_name,
        knowledge_base_id=knowledge_base_id,
        model_id=model_id,
        thresholds=thresholds,
        profile_name=profile_name,
    )

    return build_responsible_gaming_graph(
        analysis_service=risk_analysis_service,
        query_builder=knowledge_query_builder,
        retriever=knowledge_retriever,
        prompt_builder=prompt_builder,
        assessment_service=risk_assessment_service,
    )
