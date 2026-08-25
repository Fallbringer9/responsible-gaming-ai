from datetime import UTC, datetime
from decimal import Decimal

from responsible_gaming.bootstrap.composition_root import (
    RiskThresholds,
    build_analyze_player_use_case,
)
from responsible_gaming.config.settings import Settings
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot


def main() -> None:
    settings = Settings.from_env()

    use_case = build_analyze_player_use_case(
        region_name=settings.aws_region,
        knowledge_base_id=settings.bedrock_knowledge_base_id,
        model_id=settings.bedrock_model_id,
        profile_name=settings.aws_profile,
        thresholds=RiskThresholds(
            high_deposit=Decimal("1000"),
            frequent_deposit=5,
            night_session=3,
            limit_increase=1,
            failed_deposit=3,
            cancelled_withdrawal=2,
        ),
    )

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

    assessment = use_case.execute(snapshot)

    print("\n=== END-TO-END RISK ASSESSMENT ===")
    print(f"Player: {snapshot.player_id}")
    print(f"Risk level: {assessment.risk_level}")
    print(f"Confidence: {assessment.confidence}")
    print(f"Reasoning: {assessment.reasoning}")
    print(f"Summary: {assessment.recommendation.summary}")

    print("\n=== RECOMMENDED ACTIONS ===")

    for action in assessment.recommendation.actions:
        print(f"- {action.title}")
        print(f"  Priority: {action.priority}")
        print(f"  Category: {action.category}")
        print(f"  Description: {action.description}")


if __name__ == "__main__":
    main()
