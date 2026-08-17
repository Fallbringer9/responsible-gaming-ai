from datetime import UTC, datetime
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
from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery
from responsible_gaming.application.use_cases.analyze_player_use_case import (
    AnalyzePlayerUseCase,
)
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult


class FakeRiskAnalysisService:
    def __init__(self, result: RiskAnalysisResult) -> None:
        self.result = result
        self.received_snapshot = None

    def analyze(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskAnalysisResult:
        self.received_snapshot = snapshot
        return self.result


class FakeKnowledgeQueryBuilder:
    def __init__(self, query: KnowledgeQuery) -> None:
        self.query = query
        self.received_analysis = None

    def build(
        self,
        analysis: RiskAnalysisResult,
    ) -> KnowledgeQuery:
        self.received_analysis = analysis
        return self.query


class FakeKnowledgeRetriever:
    def __init__(
        self,
        documents: tuple[KnowledgeDocument, ...],
    ) -> None:
        self.documents = documents
        self.received_query = None

    def retrieve(
        self,
        query: KnowledgeQuery,
    ) -> tuple[KnowledgeDocument, ...]:
        self.received_query = query
        return self.documents


class FakePromptBuilder:
    def __init__(self, prompt: Prompt) -> None:
        self.prompt = prompt
        self.received_analysis = None
        self.received_documents = None

    def build(
        self,
        analysis: RiskAnalysisResult,
        documents: tuple[KnowledgeDocument, ...],
    ) -> Prompt:
        self.received_analysis = analysis
        self.received_documents = documents
        return self.prompt


class FakeRiskAssessmentService:
    def __init__(self, assessment: RiskAssessment) -> None:
        self.assessment = assessment
        self.received_prompt = None

    def assess(
        self,
        prompt: Prompt,
    ) -> RiskAssessment:
        self.received_prompt = prompt
        return self.assessment


def create_snapshot() -> PlayerActivitySnapshot:
    return PlayerActivitySnapshot(
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
        failed_deposit_attempt_count=0,
        cancelled_withdrawal_count=0,
    )


def create_assessment() -> RiskAssessment:
    recommendation = Recommendation(
        summary="Surveillance recommandée.",
        actions=(
            RecommendationAction(
                title="Contacter le joueur",
                description="Effectuer un contact humain.",
                priority=RecommendationPriority.HIGH,
                category=RecommendationCategory.HUMAN_CONTACT,
            ),
        ),
    )

    return RiskAssessment(
        risk_level=RiskLevel.HIGH,
        confidence=0.91,
        reasoning="Plusieurs signaux nécessitent une attention.",
        recommendation=recommendation,
    )


def test_execute_returns_risk_assessment() -> None:
    snapshot = create_snapshot()

    analysis = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(),
    )

    query = KnowledgeQuery(
        text="Prévention du jeu excessif",
    )

    documents = (
        KnowledgeDocument(
            title="Cadre de référence ANJ",
            source="s3://test/anj.pdf",
            content="Document de prévention du jeu excessif.",
            metadata={"category": "regulation"},
        ),
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse ce joueur.",
    )

    expected_assessment = create_assessment()

    use_case = AnalyzePlayerUseCase(
        risk_analysis_service=FakeRiskAnalysisService(analysis),
        knowledge_query_builder=FakeKnowledgeQueryBuilder(query),
        knowledge_retriever=FakeKnowledgeRetriever(documents),
        prompt_builder=FakePromptBuilder(prompt),
        risk_assessment_service=FakeRiskAssessmentService(
            expected_assessment,
        ),
    )

    result = use_case.execute(snapshot)

    assert result == expected_assessment


def test_execute_passes_outputs_to_next_pipeline_step() -> None:
    snapshot = create_snapshot()

    analysis = RiskAnalysisResult(
        snapshot=snapshot,
        signals=(),
    )

    query = KnowledgeQuery(
        text="Prévention du jeu excessif",
    )

    documents = (
        KnowledgeDocument(
            title="Cadre de référence ANJ",
            source="s3://test/anj.pdf",
            content="Document de prévention du jeu excessif.",
            metadata={"category": "regulation"},
        ),
    )

    prompt = Prompt(
        system_prompt="Tu es un expert en jeu responsable.",
        user_prompt="Analyse ce joueur.",
    )

    expected_assessment = create_assessment()

    risk_analysis_service = FakeRiskAnalysisService(analysis)
    query_builder = FakeKnowledgeQueryBuilder(query)
    knowledge_retriever = FakeKnowledgeRetriever(documents)
    prompt_builder = FakePromptBuilder(prompt)
    risk_assessment_service = FakeRiskAssessmentService(
        expected_assessment,
    )

    use_case = AnalyzePlayerUseCase(
        risk_analysis_service=risk_analysis_service,
        knowledge_query_builder=query_builder,
        knowledge_retriever=knowledge_retriever,
        prompt_builder=prompt_builder,
        risk_assessment_service=risk_assessment_service,
    )

    result = use_case.execute(snapshot)

    assert risk_analysis_service.received_snapshot is snapshot
    assert query_builder.received_analysis is analysis
    assert knowledge_retriever.received_query is query

    assert prompt_builder.received_analysis is analysis
    assert prompt_builder.received_documents is documents

    assert risk_assessment_service.received_prompt is prompt

    assert result is expected_assessment
