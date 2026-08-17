from dataclasses import dataclass

from responsible_gaming.application.ai.prompt_builder import PromptBuilder
from responsible_gaming.application.ai.risk_assessment import RiskAssessment
from responsible_gaming.application.ai.risk_assessment_service import (
    RiskAssessmentService,
)
from responsible_gaming.application.rag.knowledge_query_builder import (
    KnowledgeQueryBuilder,
)
from responsible_gaming.application.rag.retrieve_knowledge_service import (
    RetrieveKnowledgeService,
)
from responsible_gaming.domain.player_activity import PlayerActivitySnapshot
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService


@dataclass(frozen=True, slots=True)
class AnalyzePlayerUseCase:
    risk_analysis_service: RiskAnalysisService
    knowledge_query_builder: KnowledgeQueryBuilder
    knowledge_retriever: RetrieveKnowledgeService
    prompt_builder: PromptBuilder
    risk_assessment_service: RiskAssessmentService

    def execute(
        self,
        snapshot: PlayerActivitySnapshot,
    ) -> RiskAssessment:
        analysis = self.risk_analysis_service.analyze(snapshot)

        query = self.knowledge_query_builder.build(analysis)

        documents = self.knowledge_retriever.retrieve(query)

        prompt = self.prompt_builder.build(
            analysis,
            documents,
        )

        return self.risk_assessment_service.assess(prompt)
