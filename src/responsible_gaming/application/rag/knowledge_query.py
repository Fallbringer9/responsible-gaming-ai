from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeQuery:
    """Represents a retrieval query sent to the knowledge base."""

    text: str
