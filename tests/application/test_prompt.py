import pytest

from responsible_gaming.application.ai.prompt import Prompt


def build_prompt(**overrides: object) -> Prompt:
    values = {
        "system_prompt": ("You are a responsible gaming assistant."),
        "user_prompt": ("Analyse the player activity and provide recommendations."),
    }

    values.update(overrides)

    return Prompt(**values)


def test_create_valid_prompt() -> None:
    prompt = build_prompt()

    assert prompt.system_prompt == "You are a responsible gaming assistant."

    assert (
        prompt.user_prompt == "Analyse the player activity and provide recommendations."
    )


def test_trim_prompt_fields() -> None:
    prompt = build_prompt(
        system_prompt="  System prompt  ",
        user_prompt="  User prompt  ",
    )

    assert prompt.system_prompt == "System prompt"
    assert prompt.user_prompt == "User prompt"


def test_raise_when_system_prompt_is_empty() -> None:
    with pytest.raises(
        ValueError,
        match="system_prompt must not be empty",
    ):
        build_prompt(system_prompt="   ")


def test_raise_when_user_prompt_is_empty() -> None:
    with pytest.raises(
        ValueError,
        match="user_prompt must not be empty",
    ):
        build_prompt(user_prompt="   ")
