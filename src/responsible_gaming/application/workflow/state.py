from typing import NotRequired, TypedDict


class PlayerActivitySnapshotState(TypedDict):
    player_id: str
    period_start: str
    period_end: str
    deposit_count: int
    total_deposit_amount: str
    total_withdrawal_amount: str
    total_wager_amount: str
    total_win_amount: str
    session_count: int
    nighttime_session_count: int
    limit_increase_request_count: int
    failed_deposit_attempt_count: int
    cancelled_withdrawal_count: int


class RiskSignalState(TypedDict):
    code: str
    severity: str
    observed_value: str
    threshold: str


class RiskAnalysisState(TypedDict):
    snapshot: PlayerActivitySnapshotState
    signals: list[RiskSignalState]


class KnowledgeDocumentState(TypedDict):
    title: str
    source: str
    content: str
    metadata: dict[str, object]


class PromptState(TypedDict):
    system_prompt: str
    user_prompt: str


class RecommendationActionState(TypedDict):
    title: str
    description: str
    priority: str
    category: str


class RecommendationState(TypedDict):
    summary: str
    actions: list[RecommendationActionState]


class RiskAssessmentState(TypedDict):
    risk_level: str
    confidence: float
    reasoning: str
    recommendation: RecommendationState


class ResponsibleGamingState(TypedDict):
    snapshot: PlayerActivitySnapshotState

    analysis: NotRequired[RiskAnalysisState]
    documents: NotRequired[list[KnowledgeDocumentState]]
    prompt: NotRequired[PromptState]
    assessment: NotRequired[RiskAssessmentState]

    human_review_required: NotRequired[bool]
