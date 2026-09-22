import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from responsible_gaming.application.review.review_request import ReviewRequest


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    review_request = ReviewRequest.model_validate(event)

    table_name = os.environ["ASSESSMENT_TABLE_NAME"]

    dynamodb = boto3.client("dynamodb")

    try:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                "assessment_id": {
                    "S": review_request.assessment_id,
                },
                "assessment": {
                    "S": json.dumps(review_request.assessment),
                },
                "human_review_required": {
                    "BOOL": True,
                },
                "review_status": {
                    "S": "PENDING",
                },
                "task_token": {
                    "S": review_request.task_token,
                },
            },
            ConditionExpression="attribute_not_exists(assessment_id)",
        )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")

        if error_code == "ConditionalCheckFailedException":
            raise RuntimeError(
                f"Review already exists for assessment {review_request.assessment_id}"
            ) from error

        raise

    return {
        "assessment_id": review_request.assessment_id,
        "review_status": "PENDING",
    }
