from typing import Protocol

from responsible_gaming.application.ai.prompt import Prompt
from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.domain.risk_analysis_result import (
    RiskAnalysisResult,
)


class PromptBuilder(Protocol):
    """Builds a prompt from a deterministic risk analysis."""

    def build(
        self,
        analysis: RiskAnalysisResult,
        documents: tuple[KnowledgeDocument, ...],
    ) -> Prompt: ...
