from typing import Protocol

from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.domain.risk_analysis_result import (
    RiskAnalysisResult,
)


class RetrieveKnowledgeService(Protocol):
    """Retrieves knowledge documents relevant to a risk analysis."""

    def retrieve(
        self,
        analysis: RiskAnalysisResult,
    ) -> tuple[KnowledgeDocument, ...]: ...
