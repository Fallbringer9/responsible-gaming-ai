from typing import Protocol

from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery


class RetrieveKnowledgeService(Protocol):
    """Retrieves knowledge documents relevant to a knowledge query."""

    def retrieve(
        self,
        query: KnowledgeQuery,
    ) -> tuple[KnowledgeDocument, ...]: ...
