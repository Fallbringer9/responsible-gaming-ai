import json
import os
from decimal import Decimal
from functools import lru_cache
from typing import Any

import boto3

from responsible_gaming.application.workflow.state import (
    ResponsibleGamingState,
)
from responsible_gaming.bootstrap.composition_root import (
    RiskThresholds,
    build_responsible_gaming_workflow,
)

s3_client = boto3.client("s3")


@lru_cache(maxsize=1)
def _get_graph():
    return build_responsible_gaming_workflow(
        region_name=os.environ["AWS_REGION"],
        knowledge_base_id=os.environ["KNOWLEDGE_BASE_ID"],
        model_id=os.environ["MODEL_ID"],
        thresholds=RiskThresholds(
            high_deposit=Decimal("1000"),
            frequent_deposit=5,
            night_session=3,
            limit_increase=1,
            failed_deposit=3,
            cancelled_withdrawal=2,
        ),
    )


def _load_snapshot(
    bucket: str,
    key: str,
) -> dict[str, Any]:
    response = s3_client.get_object(
        Bucket=bucket,
        Key=key,
    )

    body = response["Body"].read()

    return json.loads(body)


def handler(
    event: dict[str, Any],
    context: Any,
) -> dict[str, Any]:
    assessment_id = event["assessment_id"]

    bucket = event["input"]["bucket"]
    key = event["input"]["key"]

    snapshot = _load_snapshot(
        bucket=bucket,
        key=key,
    )

    initial_state: ResponsibleGamingState = {
        "snapshot": snapshot,
    }

    graph = _get_graph()

    result = graph.invoke(initial_state)

    return {
        "assessment_id": assessment_id,
        "assessment": result["assessment"],
        "human_review_required": result["human_review_required"],
    }
