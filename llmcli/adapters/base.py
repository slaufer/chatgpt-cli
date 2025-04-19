from typing import Any, Callable, Iterable, Optional, Tuple
from llmcli.messages.message import Message


class BaseApiAdapter:
    NAME = "base"
    HR_NAME = "Base API Adapter"
    OPTIONS = []
    MASKED_OPTIONS = set()

    def __init__(self, params: dict) -> None:
        self.config = {}

        for option in self.OPTIONS:
            if option.name in params:
                self.config[option.name] = params[option.name]
            elif option.default is not None:
                self.config[option.name] = option.default

    def get_completion(
        self, input_messages: list[Message]
    ) -> Tuple[Iterable[str] | None, Message]:
        raise NotImplementedError("get_completion() must be implemented in a subclass")

    def get_display_name(self) -> str:
        model = self.config.get("model")

        if model is not None:
            return f"{self.HR_NAME} / {model}"

        return f"{self.HR_NAME}"

    def get_config(
        self,
        key: str,
        cast: Optional[Callable[[str], Any]] = None,
        default: Optional[Any] = None
    ) -> Optional[Any]:
        value = self.config.get(key)

        if value is None:
            return default

        if cast is None:
            return value

        try:
            return cast(value)
        except (ValueError, TypeError, KeyError):
            return default

    def get_masked_config(self) -> dict[str, str]:
        return {k: v for k, v in self.config.items() if k not in self.MASKED_OPTIONS}


# pylint: disable=too-few-public-methods
class ApiAdapterOption:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        hr_name: str,
        description: str,
        default: Any = None,
        default_help_override: str | None = None,
    ) -> None:
        self.name = name
        self.hr_name = hr_name
        self.description = description
        self.default = default
        self.default_help_override = default_help_override
