import hashlib
import json
import os
from typing import Any
from urllib.parse import unquote_plus

import boto3

step_functions_client = boto3.client("stepfunctions")


def _build_assessment_id(
    bucket: str,
    key: str,
    sequencer: str,
) -> str:
    raw_id = f"{bucket}:{key}:{sequencer}"

    return hashlib.sha256(
        raw_id.encode("utf-8"),
    ).hexdigest()[:32]


def _parse_s3_event(
    sqs_record: dict[str, Any],
) -> tuple[str, str, str]:
    body = json.loads(sqs_record["body"])

    s3_record = body["Records"][0]

    bucket = s3_record["s3"]["bucket"]["name"]
    key = unquote_plus(
        s3_record["s3"]["object"]["key"],
    )
    sequencer = s3_record["s3"]["object"]["sequencer"]

    return bucket, key, sequencer


def _start_workflow(
    bucket: str,
    key: str,
    sequencer: str,
) -> None:
    assessment_id = _build_assessment_id(
        bucket=bucket,
        key=key,
        sequencer=sequencer,
    )

    workflow_input = {
        "assessment_id": assessment_id,
        "input": {
            "bucket": bucket,
            "key": key,
        },
    }

    step_functions_client.start_execution(
        stateMachineArn=os.environ["STATE_MACHINE_ARN"],
        name=f"assessment-{assessment_id}",
        input=json.dumps(workflow_input),
    )


def handler(
    event: dict[str, Any],
    context: Any,
) -> dict[str, list[dict[str, str]]]:
    batch_failures = []

    for record in event["Records"]:
        try:
            bucket, key, sequencer = _parse_s3_event(
                record,
            )

            _start_workflow(
                bucket=bucket,
                key=key,
                sequencer=sequencer,
            )

        except Exception:
            batch_failures.append(
                {
                    "itemIdentifier": record["messageId"],
                }
            )

    return {
        "batchItemFailures": batch_failures,
    }
