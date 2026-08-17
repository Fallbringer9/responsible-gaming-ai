from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery
from responsible_gaming.application.rag.knowledge_query_builder import (
    KnowledgeQueryBuilder,
)
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult


class DefaultKnowledgeQueryBuilder(KnowledgeQueryBuilder):
    """Builds a retrieval query from a deterministic risk analysis."""

    def build(
        self,
        analysis: RiskAnalysisResult,
    ) -> KnowledgeQuery:
        titles = [signal.title for signal in analysis.signals]

        return KnowledgeQuery(
            text="\n".join(titles),
        )
