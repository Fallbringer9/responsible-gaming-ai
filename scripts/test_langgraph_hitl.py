from datetime import UTC, datetime
from decimal import Decimal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

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
from responsible_gaming.application.workflow.graph import (
    build_responsible_gaming_graph,
)
from responsible_gaming.application.workflow.state_mapper import (
    assessment_from_state,
    snapshot_to_state,
)
from responsible_gaming.config.settings import Settings
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
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService


def main() -> None:
    settings = Settings.from_env()

    client_factory = BedrockClientFactory(
        region_name=settings.aws_region,
        profile_name=settings.aws_profile,
    )

    analysis_service = RiskAnalysisService(
        detectors=(
            HighDepositDetector(
                threshold=Decimal("1000"),
            ),
            FrequentDepositDetector(
                threshold=5,
            ),
            NightSessionDetector(
                threshold=3,
            ),
            LimitIncreaseDetector(
                threshold=1,
            ),
            FailedDepositDetector(
                threshold=3,
            ),
            CancelledWithdrawalDetector(
                threshold=2,
            ),
        ),
    )

    query_builder = DefaultKnowledgeQueryBuilder()

    retriever = BedrockKnowledgeRetriever(
        client=client_factory.create_knowledge_base_client(),
        knowledge_base_id=settings.bedrock_knowledge_base_id,
    )

    prompt_builder = DefaultPromptBuilder()

    assessment_service = BedrockRiskAssessmentService(
        client=client_factory.create_runtime_client(),
        model_id=settings.bedrock_model_id,
    )

    checkpointer = InMemorySaver()

    graph = build_responsible_gaming_graph(
        analysis_service=analysis_service,
        query_builder=query_builder,
        retriever=retriever,
        prompt_builder=prompt_builder,
        assessment_service=assessment_service,
        checkpointer=checkpointer,
    )

    snapshot = PlayerActivitySnapshot(
        player_id="langgraph-integration-test-player",
        period_start=datetime(
            2026,
            8,
            1,
            tzinfo=UTC,
        ),
        period_end=datetime(
            2026,
            8,
            8,
            tzinfo=UTC,
        ),
        deposit_count=12,
        total_deposit_amount=Decimal("1800"),
        total_withdrawal_amount=Decimal("200"),
        total_wager_amount=Decimal("2500"),
        total_win_amount=Decimal("600"),
        session_count=15,
        nighttime_session_count=6,
        limit_increase_request_count=2,
        failed_deposit_attempt_count=4,
        cancelled_withdrawal_count=3,
    )

    config = {
        "configurable": {
            "thread_id": "langgraph-integration-test-player",
        }
    }

    print("\n=== START GRAPH ===")

    result = graph.invoke(
        {
            "snapshot": snapshot_to_state(snapshot),
        },
        config=config,
    )

    if "__interrupt__" in result:
        print("\n=== GRAPH PAUSED FOR HUMAN REVIEW ===")

        for interruption in result["__interrupt__"]:
            print(interruption.value)

        print("\n=== RESUMING GRAPH ===")

        result = graph.invoke(
            Command(
                resume={
                    "approved": True,
                    "comment": (
                        "Assessment reviewed and approved "
                        "by responsible gaming operator."
                    ),
                }
            ),
            config=config,
        )

    print("\n=== GRAPH COMPLETED ===")

    assessment = assessment_from_state(
        result["assessment"],
    )

    print(f"Risk level: {assessment.risk_level.value}")
    print(f"Confidence: {assessment.confidence}")
    print(f"Summary: {assessment.recommendation.summary}")

    human_decision = result.get(
        "human_review_decision",
    )

    if human_decision is not None:
        print("\n=== HUMAN REVIEW ===")
        print(f"Approved: {human_decision['approved']}")
        print(f"Comment: {human_decision['comment']}")


if __name__ == "__main__":
    main()
