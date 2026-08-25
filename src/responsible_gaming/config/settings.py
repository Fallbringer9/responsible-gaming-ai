import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    aws_profile: str
    aws_region: str
    bedrock_knowledge_base_id: str
    bedrock_model_id: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        aws_profile = os.getenv("AWS_PROFILE")
        aws_region = os.getenv("AWS_REGION")
        knowledge_base_id = os.getenv(
            "BEDROCK_KNOWLEDGE_BASE_ID",
        )
        model_id = os.getenv("BEDROCK_MODEL_ID")

        if not aws_profile:
            raise ValueError("AWS_PROFILE must be configured")

        if not aws_region:
            raise ValueError("AWS_REGION must be configured")

        if not knowledge_base_id:
            raise ValueError("BEDROCK_KNOWLEDGE_BASE_ID must be configured")

        if not model_id:
            raise ValueError("BEDROCK_MODEL_ID must be configured")

        return cls(
            aws_profile=aws_profile,
            aws_region=aws_region,
            bedrock_knowledge_base_id=knowledge_base_id,
            bedrock_model_id=model_id,
        )
