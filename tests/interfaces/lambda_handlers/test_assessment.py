import json
from io import BytesIO

from responsible_gaming.interfaces.lambda_handlers import assessment


class FakeS3Client:
    def __init__(self, snapshot: dict) -> None:
        self.snapshot = snapshot
        self.received_bucket = None
        self.received_key = None

    def get_object(
        self,
        *,
        Bucket: str,
        Key: str,
    ) -> dict:
        self.received_bucket = Bucket
        self.received_key = Key

        return {"Body": BytesIO(json.dumps(self.snapshot).encode("utf-8"))}


class FakeGraph:
    def __init__(self, result: dict) -> None:
        self.result = result
        self.received_state = None

    def invoke(self, state: dict) -> dict:
        self.received_state = state
        return self.result


def test_handler_loads_snapshot_and_runs_graph(
    monkeypatch,
) -> None:
    snapshot = {
        "player_id": "player-123",
        "period_start": "2026-08-01T00:00:00+00:00",
        "period_end": "2026-08-02T00:00:00+00:00",
        "deposit_count": 12,
        "total_deposit_amount": "1800",
        "total_withdrawal_amount": "100",
        "total_wager_amount": "2000",
        "total_win_amount": "500",
        "session_count": 8,
        "nighttime_session_count": 6,
        "limit_increase_request_count": 2,
        "failed_deposit_attempt_count": 4,
        "cancelled_withdrawal_count": 3,
    }

    fake_s3 = FakeS3Client(
        snapshot=snapshot,
    )

    fake_graph = FakeGraph(
        result={
            "assessment": {
                "risk_level": "CRITICAL",
                "confidence": 0.95,
                "reasoning": "Test reasoning.",
                "recommendation": {
                    "summary": "Immediate intervention.",
                    "actions": [
                        {
                            "title": "Contact player",
                            "description": "Human review required.",
                            "priority": "HIGH",
                            "category": "HUMAN_REVIEW",
                        }
                    ],
                },
            },
            "human_review_required": True,
        }
    )

    monkeypatch.setattr(
        assessment,
        "s3_client",
        fake_s3,
    )

    monkeypatch.setattr(
        assessment,
        "_get_graph",
        lambda: fake_graph,
    )

    event = {
        "assessment_id": "assessment-123",
        "input": {
            "bucket": "responsible-gaming-input-dev",
            "key": "snapshots/player-123.json",
        },
    }

    result = assessment.handler(
        event=event,
        context=None,
    )

    assert fake_s3.received_bucket == ("responsible-gaming-input-dev")

    assert fake_s3.received_key == ("snapshots/player-123.json")

    assert fake_graph.received_state == {
        "snapshot": snapshot,
    }

    assert result == {
        "assessment_id": "assessment-123",
        "assessment": {
            "risk_level": "CRITICAL",
            "confidence": 0.95,
            "reasoning": "Test reasoning.",
            "recommendation": {
                "summary": "Immediate intervention.",
                "actions": [
                    {
                        "title": "Contact player",
                        "description": "Human review required.",
                        "priority": "HIGH",
                        "category": "HUMAN_REVIEW",
                    }
                ],
            },
        },
        "human_review_required": True,
    }
