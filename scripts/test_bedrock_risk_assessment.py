from datetime import UTC, datetime
from decimal import Decimal

from responsible_gaming.adapters.bedrock.bedrock_client_factory import (
    BedrockClientFactory,
)
from responsible_gaming.adapters.bedrock.bedrock_risk_assessment_service import (
    BedrockRiskAssessmentService,
)
from responsible_gaming.application.ai.default_prompt_builder import (
    DefaultPromptBuilder,
)
from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
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

    snapshot = PlayerActivitySnapshot(
        player_id="integration-test-player",
        period_start=datetime(2026, 8, 1, tzinfo=UTC),
        period_end=datetime(2026, 8, 8, tzinfo=UTC),
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

    risk_analysis_service = RiskAnalysisService(
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

    analysis = risk_analysis_service.analyze(snapshot)

    documents = (
        KnowledgeDocument(
            title="Cadre de référence ANJ",
            source="s3://integration-test/anj.pdf",
            content=(
                "Operators should consider multiple indicators together, "
                "including gambling frequency, gambling intensity, spending, "
                "and changes in player behaviour."
            ),
            metadata={
                "authority": "ANJ",
                "document_type": "regulation",
            },
        ),
    )

    prompt_builder = DefaultPromptBuilder()

    prompt = prompt_builder.build(
        analysis=analysis,
        documents=documents,
    )

    client_factory = BedrockClientFactory(
        region_name=settings.aws_region,
        profile_name=settings.aws_profile,
    )

    assessment_service = BedrockRiskAssessmentService(
        client=client_factory.create_runtime_client(),
        model_id=settings.bedrock_model_id,
    )

    assessment = assessment_service.assess(prompt)

    print("\n--- Risk Assessment ---")
    print(f"Risk level: {assessment.risk_level}")
    print(f"Confidence: {assessment.confidence}")
    print(f"Reasoning: {assessment.reasoning}")
    print(f"Summary: {assessment.recommendation.summary}")

    print("\n--- Recommended Actions ---")

    for action in assessment.recommendation.actions:
        print(f"- {action.title}")
        print(f"  Priority: {action.priority}")
        print(f"  Category: {action.category}")
        print(f"  Description: {action.description}")


if __name__ == "__main__":
    main()
