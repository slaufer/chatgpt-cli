from typing import Any, Iterable, Tuple, Union
from llmcli.message import Message


class BaseApiAdapter:
    NAME = "base"
    HR_NAME = "Base API Adapter"
    OPTIONS = []
    config = {}

    def __init__(self, params: dict) -> None:
        self.config = {}

        for option in self.OPTIONS:
            if option.name in params:
                self.config[option.name] = params[option.name]
            elif option.default is not None:
                self.config[option.name] = option.default

    def get_completion(
        self, input_messages: list[Message]
    ) -> Tuple[Union[Iterable[str], None], Message]:
        raise NotImplementedError("get_completion() must be implemented in a subclass")

    def get_display_name(self) -> str:
        model = self.config.get("model")

        if model is not None:
            return f"{self.HR_NAME} / {model}"
        else:
            return f"{self.HR_NAME}"


class ApiAdapterOption:
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
