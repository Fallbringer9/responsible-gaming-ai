from typing import Protocol

from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult


class KnowledgeQueryBuilder(Protocol):
    """Builds a knowledge query from a deterministic risk analysis."""

    def build(
        self,
        analysis: RiskAnalysisResult,
    ) -> KnowledgeQuery: ...
