import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from responsible_gaming.application.review.review_decision import ReviewDecision


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    assessment_id = event.get("pathParameters", {}).get("assessment_id")

    if not assessment_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing assessment_id"}),
        }

    try:
        body = json.loads(event.get("body") or "{}")
        review_decision = ReviewDecision.model_validate(body)
    except (json.JSONDecodeError, ValidationError):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid review decision"}),
        }

    table_name = os.environ["ASSESSMENT_TABLE_NAME"]

    dynamodb = boto3.client("dynamodb")
    step_functions = boto3.client("stepfunctions")

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
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Assessment not found"}),
        }

    if "task_token" not in item:
        return {
            "statusCode": 409,
            "body": json.dumps({"error": "Review already completed"}),
        }

    task_token = item["task_token"]["S"]

    try:
        dynamodb.update_item(
            TableName=table_name,
            Key={
                "assessment_id": {
                    "S": assessment_id,
                }
            },
            UpdateExpression=(
                "SET review_status = :review_status, review_comment = :review_comment"
            ),
            ConditionExpression=(
                "review_status = :pending AND attribute_exists(task_token)"
            ),
            ExpressionAttributeValues={
                ":review_status": {
                    "S": review_decision.decision.value,
                },
                ":review_comment": {
                    "S": review_decision.comment or "",
                },
                ":pending": {
                    "S": "PENDING",
                },
            },
        )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")

        if error_code == "ConditionalCheckFailedException":
            return {
                "statusCode": 409,
                "body": json.dumps({"error": "Review already completed"}),
            }

        raise

    step_functions.send_task_success(
        taskToken=task_token,
        output=json.dumps(
            {
                "assessment_id": assessment_id,
                "assessment": json.loads(item["assessment"]["S"]),
                "human_review_required": True,
                "review_status": review_decision.decision.value,
            }
        ),
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "assessment_id": assessment_id,
                "review_status": review_decision.decision.value,
            }
        ),
    }
