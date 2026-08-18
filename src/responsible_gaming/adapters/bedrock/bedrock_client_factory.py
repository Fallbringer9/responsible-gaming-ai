from typing import Any

import boto3


class BedrockClientFactory:
    def __init__(
        self,
        region_name: str,
    ) -> None:
        self._region_name = region_name

    def create_knowledge_base_client(self) -> Any:
        return boto3.client(
            "bedrock-agent-runtime",
            region_name=self._region_name,
        )

    def create_runtime_client(self) -> Any:
        return boto3.client(
            "bedrock-runtime",
            region_name=self._region_name,
        )
