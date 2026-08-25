from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery
from responsible_gaming.application.rag.retrieve_knowledge_service import (
    RetrieveKnowledgeService,
)


class BedrockKnowledgeRetriever(RetrieveKnowledgeService):
    """Retrieves documents from an Amazon Bedrock Knowledge Base."""

    def __init__(
        self,
        client: Any,
        knowledge_base_id: str,
    ) -> None:
        self._client = client
        self._knowledge_base_id = knowledge_base_id

    def retrieve(
        self,
        query: KnowledgeQuery,
    ) -> tuple[KnowledgeDocument, ...]:
        response = self._client.retrieve(
            knowledgeBaseId=self._knowledge_base_id,
            retrievalQuery={
                "text": query.text,
            },
        )

        results = response.get("retrievalResults", [])

        documents = []

        for result in results:
            content = result["content"]["text"]
            source = result["location"]["s3Location"]["uri"]
            metadata = result.get("metadata", {})

            title = metadata.get("title")

            if not title:
                parsed_source = urlparse(source)
                title = PurePosixPath(parsed_source.path).name

            document = KnowledgeDocument(
                title=title,
                source=source,
                content=content,
                metadata=metadata,
            )

            documents.append(document)

        return tuple(documents)
