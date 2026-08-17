import pytest

from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)


def build_document(**overrides: object) -> KnowledgeDocument:
    values = {
        "title": "ANJ Responsible Gaming Guidelines",
        "source": "anj_guidelines_v3.pdf",
        "content": ("Players showing repeated risky behaviours should be monitored."),
        "metadata": {
            "publication_date": "2026-01-15",
            "category": "ANJ_GUIDELINE",
        },
    }

    values.update(overrides)

    return KnowledgeDocument(**values)


def test_create_valid_document() -> None:
    document = build_document()

    assert document.title == "ANJ Responsible Gaming Guidelines"

    assert document.source == "anj_guidelines_v3.pdf"

    assert (
        document.content
        == "Players showing repeated risky behaviours should be monitored."
    )

    assert document.metadata["category"] == "ANJ_GUIDELINE"


def test_trim_string_fields() -> None:
    document = build_document(
        title="  ANJ Guidelines  ",
        source="  anj.pdf  ",
        content="  Important content.  ",
    )

    assert document.title == "ANJ Guidelines"

    assert document.source == "anj.pdf"

    assert document.content == "Important content."


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("title", "   ", "title must not be empty"),
        ("source", "   ", "source must not be empty"),
        ("content", "   ", "content must not be empty"),
    ],
)
def test_empty_string_fields_are_rejected(
    field: str,
    value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        build_document(**{field: value})


def test_metadata_is_read_only() -> None:
    document = build_document()

    with pytest.raises(TypeError):
        document.metadata["category"] = "TEST"
