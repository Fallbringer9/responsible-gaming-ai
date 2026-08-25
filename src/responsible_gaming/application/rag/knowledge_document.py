from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    """Document retrieved from the knowledge base."""

    title: str
    source: str
    content: str
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", self.title.strip())
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(self, "content", self.content.strip())
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

        if not self.title:
            raise ValueError("title must not be empty")

        if not self.source:
            raise ValueError("source must not be empty")

        if not self.content:
            raise ValueError("content must not be empty")
