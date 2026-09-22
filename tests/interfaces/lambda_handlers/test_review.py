import json

import pytest
from botocore.exceptions import ClientError
from pydantic import ValidationError

from responsible_gaming.interfaces.lambda_handlers import review


class FakeDynamoDB:
    def __init__(
        self,
        *,
        conditional_failure: bool = False,
    ) -> None:
        self.put_item_calls: list[dict] = []
        self.conditional_failure = conditional_failure

    def put_item(self, **kwargs) -> None:
        self.put_item_calls.append(kwargs)

        if self.conditional_failure:
            raise ClientError(
                {
                    "Error": {
                        "Code": "ConditionalCheckFailedException",
                        "Message": "The conditional request failed",
                    }
                },
                "PutItem",
            )


def test_handler_creates_pending_review(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDB()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "assessment_id": "assessment-123",
        "assessment": {
            "risk_level": "CRITICAL",
            "confidence": 0.95,
        },
        "task_token": "task-token-123",
    }

    result = review.handler(event, None)

    assert result == {
        "assessment_id": "assessment-123",
        "review_status": "PENDING",
    }

    assert len(fake_dynamodb.put_item_calls) == 1

    call = fake_dynamodb.put_item_calls[0]

    assert call["TableName"] == "responsible-gaming-assessments-dev"
    assert call["ConditionExpression"] == ("attribute_not_exists(assessment_id)")

    item = call["Item"]

    assert item["assessment_id"]["S"] == "assessment-123"
    assert json.loads(item["assessment"]["S"]) == event["assessment"]
    assert item["human_review_required"]["BOOL"] is True
    assert item["review_status"]["S"] == "PENDING"
    assert item["task_token"]["S"] == "task-token-123"


def test_handler_rejects_invalid_review_request(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDB()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "assessment_id": "assessment-123",
        "assessment": {
            "risk_level": "CRITICAL",
        },
    }

    with pytest.raises(ValidationError):
        review.handler(event, None)

    assert fake_dynamodb.put_item_calls == []


def test_handler_rejects_duplicate_review(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDB(
        conditional_failure=True,
    )

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "assessment_id": "assessment-123",
        "assessment": {
            "risk_level": "CRITICAL",
            "confidence": 0.95,
        },
        "task_token": "task-token-456",
    }

    with pytest.raises(
        RuntimeError,
        match="Review already exists for assessment assessment-123",
    ):
        review.handler(event, None)

    assert len(fake_dynamodb.put_item_calls) == 1


def test_handler_reraises_unexpected_dynamodb_error(
    monkeypatch,
) -> None:
    class FailingDynamoDB:
        def put_item(self, **kwargs) -> None:
            raise ClientError(
                {
                    "Error": {
                        "Code": "InternalServerError",
                        "Message": "Unexpected DynamoDB failure",
                    }
                },
                "PutItem",
            )

    fake_dynamodb = FailingDynamoDB()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "assessment_id": "assessment-123",
        "assessment": {
            "risk_level": "CRITICAL",
            "confidence": 0.95,
        },
        "task_token": "task-token-123",
    }

    with pytest.raises(ClientError):
        review.handler(event, None)
