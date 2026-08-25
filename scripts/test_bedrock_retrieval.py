from responsible_gaming.adapters.bedrock.bedrock_client_factory import (
    BedrockClientFactory,
)
from responsible_gaming.adapters.bedrock.bedrock_knowledge_retriever import (
    BedrockKnowledgeRetriever,
)
from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery
from responsible_gaming.config.settings import Settings


def main() -> None:
    settings = Settings.from_env()

    client_factory = BedrockClientFactory(
        region_name=settings.aws_region,
        profile_name=settings.aws_profile,
    )

    retriever = BedrockKnowledgeRetriever(
        client=client_factory.create_knowledge_base_client(),
        knowledge_base_id=settings.bedrock_knowledge_base_id,
    )

    query = KnowledgeQuery(
        text=("Quels comportements peuvent indiquer un risque de jeu excessif ?"),
    )

    documents = retriever.retrieve(query)

    print(f"Documents retrieved: {len(documents)}")

    for index, document in enumerate(documents, start=1):
        print(f"\n--- Document {index} ---")
        print(f"Title: {document.title}")
        print(f"Source: {document.source}")
        print(f"Content: {document.content[:500]}")
        print(f"Metadata: {dict(document.metadata)}")


if __name__ == "__main__":
    main()
