from responsible_gaming.adapters.bedrock.bedrock_knowledge_retriever import (
    BedrockKnowledgeRetriever,
)
from responsible_gaming.application.rag.knowledge_query import KnowledgeQuery


class FakeBedrockClient:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.retrieve_kwargs = None

    def retrieve(self, **kwargs):
        self.retrieve_kwargs = kwargs
        return self.response


def test_retrieve_returns_empty_tuple_when_bedrock_returns_no_results() -> None:
    client = FakeBedrockClient(
        response={"retrievalResults": []},
    )

    retriever = BedrockKnowledgeRetriever(
        client=client,
        knowledge_base_id="kb-test",
    )

    query = KnowledgeQuery(
        text="Prévention du jeu excessif",
    )

    documents = retriever.retrieve(query)

    assert documents == ()


def test_retrieve_maps_bedrock_result_to_knowledge_document() -> None:
    client = FakeBedrockClient(
        response={
            "retrievalResults": [
                {
                    "content": {
                        "text": (
                            "Les opérateurs doivent détecter "
                            "les pratiques de jeu excessif."
                        )
                    },
                    "location": {
                        "type": "S3",
                        "s3Location": {
                            "uri": "s3://responsible-gaming/regulations/anj.pdf"
                        },
                    },
                    "metadata": {
                        "title": "Cadre de référence ANJ",
                        "category": "regulation",
                    },
                }
            ]
        }
    )

    retriever = BedrockKnowledgeRetriever(
        client=client,
        knowledge_base_id="kb-test",
    )

    query = KnowledgeQuery(
        text="Prévention du jeu excessif",
    )

    documents = retriever.retrieve(query)

    assert len(documents) == 1

    document = documents[0]

    assert document.title == "Cadre de référence ANJ"
    assert document.source == "s3://responsible-gaming/regulations/anj.pdf"
    assert (
        document.content
        == "Les opérateurs doivent détecter les pratiques de jeu excessif."
    )
    assert document.metadata["category"] == "regulation"


def test_retrieve_sends_query_and_knowledge_base_id_to_bedrock() -> None:
    client = FakeBedrockClient(
        response={"retrievalResults": []},
    )

    retriever = BedrockKnowledgeRetriever(
        client=client,
        knowledge_base_id="kb-test",
    )

    query = KnowledgeQuery(
        text="Prévention du jeu excessif",
    )

    retriever.retrieve(query)

    assert client.retrieve_kwargs == {
        "knowledgeBaseId": "kb-test",
        "retrievalQuery": {
            "text": "Prévention du jeu excessif",
        },
    }
