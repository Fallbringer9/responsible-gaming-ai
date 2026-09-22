import json

from botocore.exceptions import ClientError

from responsible_gaming.interfaces.lambda_handlers import review_decision


class FakeDynamoDBClient:
    def __init__(
        self,
        *,
        conditional_failure: bool = False,
    ) -> None:
        self.updated_item = None
        self.conditional_failure = conditional_failure

    def get_item(
        self,
        *,
        TableName: str,
        Key: dict,
    ) -> dict:
        return {
            "Item": {
                "assessment_id": {
                    "S": "assessment-123",
                },
                "assessment": {
                    "S": json.dumps(
                        {
                            "risk_level": "CRITICAL",
                            "confidence": 0.95,
                        }
                    ),
                },
                "task_token": {
                    "S": "task-token-123",
                },
                "review_status": {
                    "S": "PENDING",
                },
            }
        }

    def update_item(self, **kwargs) -> None:
        self.updated_item = kwargs

        if self.conditional_failure:
            raise ClientError(
                {
                    "Error": {
                        "Code": "ConditionalCheckFailedException",
                        "Message": "The conditional request failed",
                    }
                },
                "UpdateItem",
            )


class FakeStepFunctionsClient:
    def __init__(self) -> None:
        self.task_token = None
        self.output = None

    def send_task_success(
        self,
        *,
        taskToken: str,
        output: str,
    ) -> None:
        self.task_token = taskToken
        self.output = output


def test_handler_approves_review_and_resumes_workflow(
    monkeypatch,
) -> None:
    fake_dynamodb = FakeDynamoDBClient()
    fake_step_functions = FakeStepFunctionsClient()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )

    def fake_boto3_client(service_name: str):
        if service_name == "dynamodb":
            return fake_dynamodb

        if service_name == "stepfunctions":
            return fake_step_functions

        raise ValueError(f"Unexpected AWS service: {service_name}")

    monkeypatch.setattr(
        review_decision.boto3,
        "client",
        fake_boto3_client,
    )

    event = {
        "pathParameters": {
            "assessment_id": "assessment-123",
        },
        "body": json.dumps(
            {
                "decision": "APPROVED",
                "comment": "Assessment confirmed.",
            }
        ),
    }

    result = review_decision.handler(
        event=event,
        context=None,
    )

    assert fake_dynamodb.updated_item is not None

    assert fake_dynamodb.updated_item["ConditionExpression"] == (
        "review_status = :pending AND attribute_exists(task_token)"
    )

    assert (
        fake_dynamodb.updated_item["ExpressionAttributeValues"][":review_status"]["S"]
        == "APPROVED"
    )

    assert (
        fake_dynamodb.updated_item["ExpressionAttributeValues"][":pending"]["S"]
        == "PENDING"
    )

    assert fake_step_functions.task_token == "task-token-123"

    callback_output = json.loads(fake_step_functions.output)

    assert callback_output["assessment_id"] == "assessment-123"
    assert callback_output["review_status"] == "APPROVED"

    assert result["statusCode"] == 200


def test_handler_returns_404_when_assessment_does_not_exist(
    monkeypatch,
) -> None:
    class EmptyDynamoDBClient:
        def get_item(self, **kwargs) -> dict:
            return {}

    fake_dynamodb = EmptyDynamoDBClient()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )

    monkeypatch.setattr(
        review_decision.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "pathParameters": {
            "assessment_id": "unknown-assessment",
        },
        "body": json.dumps(
            {
                "decision": "APPROVED",
            }
        ),
    }

    result = review_decision.handler(
        event=event,
        context=None,
    )

    assert result["statusCode"] == 404


def test_handler_rejects_invalid_decision(
    monkeypatch,
) -> None:
    event = {
        "pathParameters": {
            "assessment_id": "assessment-123",
        },
        "body": json.dumps(
            {
                "decision": "BANANA",
            }
        ),
    }

    result = review_decision.handler(
        event=event,
        context=None,
    )

    assert result["statusCode"] == 400


def test_handler_returns_409_when_review_is_already_completed(
    monkeypatch,
) -> None:
    class CompletedReviewDynamoDBClient:
        def get_item(self, **kwargs) -> dict:
            return {
                "Item": {
                    "assessment_id": {
                        "S": "assessment-123",
                    },
                    "assessment": {
                        "S": json.dumps(
                            {
                                "risk_level": "CRITICAL",
                                "confidence": 0.95,
                            }
                        ),
                    },
                    "review_status": {
                        "S": "APPROVED",
                    },
                }
            }

    fake_dynamodb = CompletedReviewDynamoDBClient()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )

    monkeypatch.setattr(
        review_decision.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "pathParameters": {
            "assessment_id": "assessment-123",
        },
        "body": json.dumps(
            {
                "decision": "APPROVED",
                "comment": "Duplicate decision.",
            }
        ),
    }

    result = review_decision.handler(
        event=event,
        context=None,
    )

    assert result["statusCode"] == 409
    assert json.loads(result["body"]) == {
        "error": "Review already completed",
    }


def test_handler_returns_409_when_concurrent_review_wins(
    monkeypatch,
) -> None:
    fake_dynamodb = FakeDynamoDBClient(
        conditional_failure=True,
    )
    fake_step_functions = FakeStepFunctionsClient()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )

    def fake_boto3_client(service_name: str):
        if service_name == "dynamodb":
            return fake_dynamodb

        if service_name == "stepfunctions":
            return fake_step_functions

        raise ValueError(f"Unexpected AWS service: {service_name}")

    monkeypatch.setattr(
        review_decision.boto3,
        "client",
        fake_boto3_client,
    )

    event = {
        "pathParameters": {
            "assessment_id": "assessment-123",
        },
        "body": json.dumps(
            {
                "decision": "REJECTED",
                "comment": "Concurrent decision.",
            }
        ),
    }

    result = review_decision.handler(
        event=event,
        context=None,
    )

    assert result["statusCode"] == 409
    assert json.loads(result["body"]) == {
        "error": "Review already completed",
    }

    assert fake_step_functions.task_token is None
