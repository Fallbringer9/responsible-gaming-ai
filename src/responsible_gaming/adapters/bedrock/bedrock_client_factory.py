from typing import Any

import boto3


class BedrockClientFactory:
    """Creates AWS clients used by the Bedrock adapters."""

    def __init__(
        self,
        region_name: str,
        profile_name: str | None = None,
    ) -> None:
        self._region_name = region_name

        self._session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name,
        )

    def create_knowledge_base_client(self) -> Any:
        return self._session.client(
            "bedrock-agent-runtime",
        )

    def create_runtime_client(self) -> Any:
        return self._session.client(
            "bedrock-runtime",
        )
