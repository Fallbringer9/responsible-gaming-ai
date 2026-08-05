from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Prompt:
    """Prompt sent to the Large Language Model."""

    system_prompt: str
    user_prompt: str

    def __post_init__(self) -> None:
        normalized_system_prompt = self.system_prompt.strip()
        normalized_user_prompt = self.user_prompt.strip()

        object.__setattr__(
            self,
            "system_prompt",
            normalized_system_prompt,
        )

        object.__setattr__(
            self,
            "user_prompt",
            normalized_user_prompt,
        )

        if not self.system_prompt:
            raise ValueError("system_prompt must not be empty")

        if not self.user_prompt:
            raise ValueError("user_prompt must not be empty")
