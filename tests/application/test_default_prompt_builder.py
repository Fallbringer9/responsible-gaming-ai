from datetime import UTC, datetime
from decimal import Decimal

from responsible_gaming.application.ai.default_prompt_builder import (
    DefaultPromptBuilder,
)
from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


def test_build_includes_risk_signals_and_knowledge_documents() -> None:
    snapshot = PlayerActivitySnapshot(
        player_id="player-123",
        period_start=datetime(2026, 8, 1, tzinfo=UTC),
        period_end=datetime(2026, 8, 2, tzinfo=UTC),
        deposit_count=0,
        total_deposit_amount=Decimal("0"),
        total_withdrawal_amount=Decimal("0"),
        total_wager_amount=Decimal("0"),
        total_win_amount=Decimal("0"),
        session_count=0,
        nighttime_session_count=0,
        limit_increase_request_count=0,
        failed_deposit_attempt_count=5,
        cancelled_withdrawal_count=0,
    )

    signal = RiskSignal(
        code=RiskSignalCode.FAILED_DEPOSIT,
        severity=Severity.HIGH,
        observed_value=5,
        threshold=3,
    )

    analysis = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(signal,),
    )

    documents = (
        KnowledgeDocument(
            title="Cadre de référence ANJ",
            source="s3://test/anj.pdf",
            content="Les opérateurs doivent prévenir le jeu excessif.",
            metadata={
                "category": "regulation",
            },
        ),
    )

    builder = DefaultPromptBuilder()

    prompt = builder.build(
        analysis=analysis,
        documents=documents,
    )

    assert "Tentatives de dépôt refusées" in prompt.user_prompt
    assert "observed=5" in prompt.user_prompt
    assert "threshold=3" in prompt.user_prompt

    assert "Cadre de référence ANJ" in prompt.user_prompt
    assert "s3://test/anj.pdf" in prompt.user_prompt
    assert "Les opérateurs doivent prévenir le jeu excessif." in prompt.user_prompt

    assert '"risk_level"' in prompt.system_prompt
    assert "LOW | MEDIUM | HIGH | CRITICAL" in prompt.system_prompt
    assert '"confidence"' in prompt.system_prompt
    assert '"reasoning"' in prompt.system_prompt
    assert '"recommendation"' in prompt.system_prompt
    assert '"actions"' in prompt.system_prompt


def test_build_includes_guardrails_against_unsupported_values() -> None:
    snapshot = PlayerActivitySnapshot(
        player_id="player-123",
        period_start=datetime(2026, 8, 1, tzinfo=UTC),
        period_end=datetime(2026, 8, 2, tzinfo=UTC),
        deposit_count=0,
        total_deposit_amount=Decimal("0"),
        total_withdrawal_amount=Decimal("0"),
        total_wager_amount=Decimal("0"),
        total_win_amount=Decimal("0"),
        session_count=0,
        nighttime_session_count=0,
        limit_increase_request_count=0,
        failed_deposit_attempt_count=5,
        cancelled_withdrawal_count=0,
    )

    signal = RiskSignal(
        code=RiskSignalCode.FAILED_DEPOSIT,
        severity=Severity.HIGH,
        observed_value=5,
        threshold=3,
    )

    analysis = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(signal,),
    )

    documents = (
        KnowledgeDocument(
            title="Cadre de référence ANJ",
            source="s3://test/anj.pdf",
            content="Les opérateurs doivent prévenir le jeu excessif.",
            metadata={
                "category": "regulation",
            },
        ),
    )

    builder = DefaultPromptBuilder()

    prompt = builder.build(
        analysis=analysis,
        documents=documents,
    )

    assert "Never invent or infer numerical thresholds" in prompt.system_prompt
    assert "monetary amounts" in prompt.system_prompt
    assert "durations" in prompt.system_prompt
    assert "intervention parameters" in prompt.system_prompt
    assert "Recommendations must remain qualitative" in prompt.system_prompt
