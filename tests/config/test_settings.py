from responsible_gaming.config.settings import Settings


def test_from_env_loads_settings(
    monkeypatch,
) -> None:
    monkeypatch.setenv("AWS_PROFILE", "test-profile")
    monkeypatch.setenv("AWS_REGION", "eu-west-3")
    monkeypatch.setenv(
        "BEDROCK_KNOWLEDGE_BASE_ID",
        "kb-test",
    )
    monkeypatch.setenv(
        "BEDROCK_MODEL_ID",
        "model-test",
    )

    settings = Settings.from_env()

    assert settings.aws_profile == "test-profile"
    assert settings.aws_region == "eu-west-3"
    assert settings.bedrock_knowledge_base_id == "kb-test"
    assert settings.bedrock_model_id == "model-test"
