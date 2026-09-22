import json

from responsible_gaming.interfaces.lambda_handlers import review_list


class FakeDynamoDBClient:
    def __init__(self) -> None:
        self.query_calls: list[dict] = []
        self.get_item_calls: list[dict] = []
        self.response: dict = {
            "Items": [],
        }

    def query(self, **kwargs) -> dict:
        self.query_calls.append(kwargs)
        return self.response

    def get_item(self, **kwargs) -> dict:
        self.get_item_calls.append(kwargs)
        return self.response


def test_handler_lists_pending_reviews(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDBClient()
    fake_dynamodb.response = {
        "Items": [
            {
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
                    "S": "PENDING",
                },
            }
        ]
    }

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    event = {
        "queryStringParameters": None,
    }

    result = review_list.handler(event, None)

    assert result["statusCode"] == 200

    body = json.loads(result["body"])

    assert body == {
        "reviews": [
            {
                "assessment_id": "assessment-123",
                "assessment": {
                    "risk_level": "CRITICAL",
                    "confidence": 0.95,
                },
                "review_status": "PENDING",
            }
        ],
        "next_cursor": None,
    }

    assert len(fake_dynamodb.query_calls) == 1

    query = fake_dynamodb.query_calls[0]

    assert query["TableName"] == "responsible-gaming-assessments-dev"
    assert query["IndexName"] == "review_status-index"
    assert query["Limit"] == 20

    assert query["ExpressionAttributeValues"] == {
        ":review_status": {
            "S": "PENDING",
        }
    }


def test_handler_returns_next_cursor(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDBClient()

    last_evaluated_key = {
        "assessment_id": {
            "S": "assessment-123",
        },
        "review_status": {
            "S": "PENDING",
        },
    }

    fake_dynamodb.response = {
        "Items": [],
        "LastEvaluatedKey": last_evaluated_key,
    }

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    result = review_list.handler(
        {
            "queryStringParameters": {
                "limit": "10",
            }
        },
        None,
    )

    body = json.loads(result["body"])

    assert result["statusCode"] == 200
    assert body["next_cursor"] is not None

    decoded_cursor = review_list._decode_cursor(body["next_cursor"])

    assert decoded_cursor == last_evaluated_key


def test_handler_uses_cursor_as_exclusive_start_key(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDBClient()

    start_key = {
        "assessment_id": {
            "S": "assessment-123",
        },
        "review_status": {
            "S": "PENDING",
        },
    }

    cursor = review_list._encode_cursor(start_key)

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    result = review_list.handler(
        {
            "queryStringParameters": {
                "limit": "10",
                "cursor": cursor,
            }
        },
        None,
    )

    assert result["statusCode"] == 200

    query = fake_dynamodb.query_calls[0]

    assert query["Limit"] == 10
    assert query["ExclusiveStartKey"] == start_key


def test_handler_rejects_invalid_limit(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDBClient()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    result = review_list.handler(
        {
            "queryStringParameters": {
                "limit": "500",
            }
        },
        None,
    )

    assert result["statusCode"] == 400
    assert fake_dynamodb.query_calls == []


def test_handler_rejects_invalid_cursor(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDBClient()

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    result = review_list.handler(
        {
            "queryStringParameters": {
                "cursor": "%%%invalid%%%",
            }
        },
        None,
    )

    assert result["statusCode"] == 400
    assert fake_dynamodb.query_calls == []


def test_handler_returns_review_detail(monkeypatch) -> None:
    fake_dynamodb = FakeDynamoDBClient()
    fake_dynamodb.response = {
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
            "human_review_required": {
                "BOOL": True,
            },
            "review_status": {
                "S": "PENDING",
            },
            "task_token": {
                "S": "secret-step-functions-token",
            },
        }
    }

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    result = review_list.handler(
        {
            "pathParameters": {
                "assessment_id": "assessment-123",
            }
        },
        None,
    )

    assert result["statusCode"] == 200

    body = json.loads(result["body"])

    assert body == {
        "assessment_id": "assessment-123",
        "assessment": {
            "risk_level": "CRITICAL",
            "confidence": 0.95,
        },
        "human_review_required": True,
        "review_status": "PENDING",
        "review_comment": None,
    }

    assert "task_token" not in body

    assert len(fake_dynamodb.get_item_calls) == 1

    get_item = fake_dynamodb.get_item_calls[0]

    assert get_item["TableName"] == "responsible-gaming-assessments-dev"
    assert get_item["Key"] == {
        "assessment_id": {
            "S": "assessment-123",
        }
    }


def test_handler_returns_404_when_assessment_does_not_exist(
    monkeypatch,
) -> None:
    fake_dynamodb = FakeDynamoDBClient()
    fake_dynamodb.response = {}

    monkeypatch.setenv(
        "ASSESSMENT_TABLE_NAME",
        "responsible-gaming-assessments-dev",
    )
    monkeypatch.setattr(
        review_list.boto3,
        "client",
        lambda service_name: fake_dynamodb,
    )

    result = review_list.handler(
        {
            "pathParameters": {
                "assessment_id": "missing-assessment",
            }
        },
        None,
    )

    assert result["statusCode"] == 404

    assert json.loads(result["body"]) == {
        "error": "Assessment not found",
    }

    assert len(fake_dynamodb.get_item_calls) == 1
