import base64
import json
import os
from typing import Any

import boto3

from responsible_gaming.application.review.review_detail import ReviewDetail
from responsible_gaming.application.review.review_summary import ReviewSummary

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
REVIEW_STATUS_INDEX = "review_status-index"


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    assessment_id = (event.get("pathParameters") or {}).get("assessment_id")

    if assessment_id:
        return _get_review_detail(assessment_id)

    return _list_pending_reviews(event)


def _list_pending_reviews(event: dict[str, Any]) -> dict[str, Any]:
    table_name = os.environ["ASSESSMENT_TABLE_NAME"]
    query_parameters = event.get("queryStringParameters") or {}

    try:
        limit = int(query_parameters.get("limit", DEFAULT_LIMIT))
    except (TypeError, ValueError):
        return _bad_request("limit must be an integer")

    if limit < 1 or limit > MAX_LIMIT:
        return _bad_request(f"limit must be between 1 and {MAX_LIMIT}")

    query_kwargs: dict[str, Any] = {
        "TableName": table_name,
        "IndexName": REVIEW_STATUS_INDEX,
        "KeyConditionExpression": "review_status = :review_status",
        "ExpressionAttributeValues": {
            ":review_status": {
                "S": "PENDING",
            }
        },
        "ProjectionExpression": "assessment_id, assessment, review_status",
        "Limit": limit,
    }

    cursor = query_parameters.get("cursor")

    if cursor:
        try:
            query_kwargs["ExclusiveStartKey"] = _decode_cursor(cursor)
        except (ValueError, json.JSONDecodeError):
            return _bad_request("invalid cursor")

    dynamodb = boto3.client("dynamodb")
    response = dynamodb.query(**query_kwargs)

    reviews = [
        ReviewSummary(
            assessment_id=item["assessment_id"]["S"],
            assessment=json.loads(item["assessment"]["S"]),
            review_status=item["review_status"]["S"],
        ).model_dump()
        for item in response.get("Items", [])
    ]

    next_cursor = None

    if last_evaluated_key := response.get("LastEvaluatedKey"):
        next_cursor = _encode_cursor(last_evaluated_key)

    return _json_response(
        200,
        {
            "reviews": reviews,
            "next_cursor": next_cursor,
        },
    )


def _get_review_detail(assessment_id: str) -> dict[str, Any]:
    table_name = os.environ["ASSESSMENT_TABLE_NAME"]
    dynamodb = boto3.client("dynamodb")

    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            "assessment_id": {
                "S": assessment_id,
            }
        },
    )

    item = response.get("Item")

    if item is None:
        return _json_response(
            404,
            {
                "error": "Assessment not found",
            },
        )

    review = ReviewDetail(
        assessment_id=item["assessment_id"]["S"],
        assessment=json.loads(item["assessment"]["S"]),
        human_review_required=item["human_review_required"]["BOOL"],
        review_status=(item["review_status"]["S"] if "review_status" in item else None),
        review_comment=(
            item["review_comment"]["S"] if "review_comment" in item else None
        ),
    )

    return _json_response(
        200,
        review.model_dump(),
    )


def _encode_cursor(last_evaluated_key: dict[str, Any]) -> str:
    payload = json.dumps(last_evaluated_key).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def _decode_cursor(cursor: str) -> dict[str, Any]:
    payload = base64.urlsafe_b64decode(cursor.encode("utf-8"))
    decoded = json.loads(payload.decode("utf-8"))

    if not isinstance(decoded, dict):
        raise ValueError("cursor must contain a DynamoDB key")

    return decoded


def _bad_request(message: str) -> dict[str, Any]:
    return _json_response(
        400,
        {
            "error": message,
        },
    )


def _json_response(
    status_code: int,
    body: dict[str, Any],
) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
