from datetime import datetime
from decimal import Decimal

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
from responsible_gaming.application.ai.risk_level import RiskLevel
from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.application.workflow.state import (
    KnowledgeDocumentState,
    PlayerActivitySnapshotState,
    PromptState,
    RecommendationActionState,
    RecommendationState,
    RiskAnalysisState,
    RiskAssessmentState,
    RiskSignalState,
)
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult
from responsible_gaming.domain.risk_signal import RiskSignal
from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


def snapshot_to_state(
    snapshot: PlayerActivitySnapshot,
) -> PlayerActivitySnapshotState:
    return {
        "player_id": snapshot.player_id,
        "period_start": snapshot.period_start.isoformat(),
        "period_end": snapshot.period_end.isoformat(),
        "deposit_count": snapshot.deposit_count,
        "total_deposit_amount": str(snapshot.total_deposit_amount),
        "total_withdrawal_amount": str(snapshot.total_withdrawal_amount),
        "total_wager_amount": str(snapshot.total_wager_amount),
        "total_win_amount": str(snapshot.total_win_amount),
        "session_count": snapshot.session_count,
        "nighttime_session_count": snapshot.nighttime_session_count,
        "limit_increase_request_count": snapshot.limit_increase_request_count,
        "failed_deposit_attempt_count": (snapshot.failed_deposit_attempt_count),
        "cancelled_withdrawal_count": snapshot.cancelled_withdrawal_count,
    }


def snapshot_from_state(
    snapshot: PlayerActivitySnapshotState,
) -> PlayerActivitySnapshot:
    return PlayerActivitySnapshot(
        player_id=snapshot["player_id"],
        period_start=datetime.fromisoformat(snapshot["period_start"]),
        period_end=datetime.fromisoformat(snapshot["period_end"]),
        deposit_count=snapshot["deposit_count"],
        total_deposit_amount=Decimal(snapshot["total_deposit_amount"]),
        total_withdrawal_amount=Decimal(snapshot["total_withdrawal_amount"]),
        total_wager_amount=Decimal(snapshot["total_wager_amount"]),
        total_win_amount=Decimal(snapshot["total_win_amount"]),
        session_count=snapshot["session_count"],
        nighttime_session_count=snapshot["nighttime_session_count"],
        limit_increase_request_count=snapshot["limit_increase_request_count"],
        failed_deposit_attempt_count=snapshot["failed_deposit_attempt_count"],
        cancelled_withdrawal_count=snapshot["cancelled_withdrawal_count"],
    )


def signal_to_state(
    signal: RiskSignal,
) -> RiskSignalState:
    return {
        "code": signal.code.value,
        "severity": signal.severity.value,
        "observed_value": str(signal.observed_value),
        "threshold": str(signal.threshold),
    }


def signal_from_state(
    signal: RiskSignalState,
) -> RiskSignal:
    code = RiskSignalCode(signal["code"])

    if code is RiskSignalCode.HIGH_DEPOSIT:
        observed_value = Decimal(signal["observed_value"])
        threshold = Decimal(signal["threshold"])
    else:
        observed_value = int(signal["observed_value"])
        threshold = int(signal["threshold"])

    return RiskSignal(
        code=code,
        severity=Severity(signal["severity"]),
        observed_value=observed_value,
        threshold=threshold,
    )


def analysis_to_state(
    analysis: RiskAnalysisResult,
) -> RiskAnalysisState:
    return {
        "snapshot": snapshot_to_state(analysis.snapshot),
        "signals": [signal_to_state(signal) for signal in analysis.signals],
    }


def analysis_from_state(
    analysis: RiskAnalysisState,
) -> RiskAnalysisResult:
    return RiskAnalysisResult(
        snapshot=snapshot_from_state(analysis["snapshot"]),
        signals=tuple(signal_from_state(signal) for signal in analysis["signals"]),
    )


def document_to_state(
    document: KnowledgeDocument,
) -> KnowledgeDocumentState:
    return {
        "title": document.title,
        "source": document.source,
        "content": document.content,
        "metadata": dict(document.metadata),
    }


def document_from_state(
    document: KnowledgeDocumentState,
) -> KnowledgeDocument:
    return KnowledgeDocument(
        title=document["title"],
        source=document["source"],
        content=document["content"],
        metadata=document["metadata"],
    )


def documents_to_state(
    documents: tuple[KnowledgeDocument, ...],
) -> list[KnowledgeDocumentState]:
    return [document_to_state(document) for document in documents]


def documents_from_state(
    documents: list[KnowledgeDocumentState],
) -> tuple[KnowledgeDocument, ...]:
    return tuple(document_from_state(document) for document in documents)


def prompt_to_state(
    prompt: Prompt,
) -> PromptState:
    return {
        "system_prompt": prompt.system_prompt,
        "user_prompt": prompt.user_prompt,
    }


def prompt_from_state(
    prompt: PromptState,
) -> Prompt:
    return Prompt(
        system_prompt=prompt["system_prompt"],
        user_prompt=prompt["user_prompt"],
    )


def recommendation_action_to_state(
    action: RecommendationAction,
) -> RecommendationActionState:
    return {
        "title": action.title,
        "description": action.description,
        "priority": action.priority.value,
        "category": action.category.value,
    }


def recommendation_action_from_state(
    action: RecommendationActionState,
) -> RecommendationAction:
    return RecommendationAction(
        title=action["title"],
        description=action["description"],
        priority=RecommendationPriority(action["priority"]),
        category=RecommendationCategory(action["category"]),
    )


def recommendation_to_state(
    recommendation: Recommendation,
) -> RecommendationState:
    return {
        "summary": recommendation.summary,
        "actions": [
            recommendation_action_to_state(action) for action in recommendation.actions
        ],
    }


def recommendation_from_state(
    recommendation: RecommendationState,
) -> Recommendation:
    return Recommendation(
        summary=recommendation["summary"],
        actions=tuple(
            recommendation_action_from_state(action)
            for action in recommendation["actions"]
        ),
    )


def assessment_to_state(
    assessment: RiskAssessment,
) -> RiskAssessmentState:
    return {
        "risk_level": assessment.risk_level.value,
        "confidence": assessment.confidence,
        "reasoning": assessment.reasoning,
        "recommendation": recommendation_to_state(assessment.recommendation),
    }


def assessment_from_state(
    assessment: RiskAssessmentState,
) -> RiskAssessment:
    return RiskAssessment(
        risk_level=RiskLevel(assessment["risk_level"]),
        confidence=assessment["confidence"],
        reasoning=assessment["reasoning"],
        recommendation=recommendation_from_state(assessment["recommendation"]),
    )
