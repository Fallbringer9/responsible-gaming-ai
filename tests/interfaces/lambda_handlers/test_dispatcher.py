import json

from responsible_gaming.interfaces.lambda_handlers import dispatcher

TEST_STATE_MACHINE_ARN = "arn:aws:states:eu-west-3:123456789012:stateMachine:test"


class FakeStepFunctionsClient:
    def __init__(self) -> None:
        self.executions = []

    def start_execution(self, **kwargs) -> None:
        self.executions.append(kwargs)


def build_sqs_record(
    message_id: str = "message-123",
    bucket: str = "responsible-gaming-input-dev",
    key: str = "snapshots/player-123.json",
    sequencer: str = "001",
) -> dict:
    s3_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": bucket,
                    },
                    "object": {
                        "key": key,
                        "sequencer": sequencer,
                    },
                }
            }
        ]
    }

    return {
        "messageId": message_id,
        "body": json.dumps(s3_event),
    }


def test_handler_starts_step_functions_execution(
    monkeypatch,
) -> None:
    client = FakeStepFunctionsClient()

    monkeypatch.setenv(
        "STATE_MACHINE_ARN",
        TEST_STATE_MACHINE_ARN,
    )

    monkeypatch.setattr(
        dispatcher,
        "step_functions_client",
        client,
    )

    event = {
        "Records": [
            build_sqs_record(),
        ]
    }

    result = dispatcher.handler(
        event=event,
        context=None,
    )

    assert result == {
        "batchItemFailures": [],
    }

    assert len(client.executions) == 1

    execution = client.executions[0]

    assert execution["stateMachineArn"] == TEST_STATE_MACHINE_ARN

    workflow_input = json.loads(
        execution["input"],
    )

    assert workflow_input["input"] == {
        "bucket": "responsible-gaming-input-dev",
        "key": "snapshots/player-123.json",
    }

    assert "assessment_id" in workflow_input

    assert execution["name"] == (f"assessment-{workflow_input['assessment_id']}")


def test_same_s3_event_produces_same_assessment_id() -> None:
    first_id = dispatcher._build_assessment_id(
        bucket="responsible-gaming-input-dev",
        key="snapshots/player-123.json",
        sequencer="001",
    )

    second_id = dispatcher._build_assessment_id(
        bucket="responsible-gaming-input-dev",
        key="snapshots/player-123.json",
        sequencer="001",
    )

    assert first_id == second_id


def test_different_s3_event_produces_different_assessment_id() -> None:
    first_id = dispatcher._build_assessment_id(
        bucket="responsible-gaming-input-dev",
        key="snapshots/player-123.json",
        sequencer="001",
    )

    second_id = dispatcher._build_assessment_id(
        bucket="responsible-gaming-input-dev",
        key="snapshots/player-123.json",
        sequencer="002",
    )

    assert first_id != second_id


def test_handler_reports_only_failed_message(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "STATE_MACHINE_ARN",
        TEST_STATE_MACHINE_ARN,
    )

    class FailingStepFunctionsClient:
        def start_execution(self, **kwargs) -> None:
            workflow_input = json.loads(
                kwargs["input"],
            )

            if workflow_input["input"]["key"] == "broken.json":
                raise RuntimeError("Step Functions unavailable")

    monkeypatch.setattr(
        dispatcher,
        "step_functions_client",
        FailingStepFunctionsClient(),
    )

    event = {
        "Records": [
            build_sqs_record(
                message_id="message-ok",
                key="valid.json",
            ),
            build_sqs_record(
                message_id="message-failed",
                key="broken.json",
            ),
        ]
    }

    result = dispatcher.handler(
        event=event,
        context=None,
    )

    assert result == {
        "batchItemFailures": [
            {
                "itemIdentifier": "message-failed",
            }
        ],
    }
