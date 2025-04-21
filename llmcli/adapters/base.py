"""
This module defines the base classes and utilities for API adapters.

It includes the `BaseApiAdapter` class, which serves as a foundation for implementing
specific API adapters, and the `ApiAdapterOption` class, which represents configuration
options for the adapters.
"""
from typing import Any, Callable, Iterable, Tuple
from llmcli.messages.message import Message


class BaseApiAdapter:
    """
    Base class for all API adapters.

    Parameters
    ----------
    params : dict
        A dictionary of parameters for the adapter, corresponding to the options defined in the
        adapter's OPTIONS attribute.
    """
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
        self,
        input_messages: list[Message],
    ) -> Tuple[Iterable[str] | None, Message]:
        """
        Get a completion from the API.

        Parameters
        ----------
        input_messages : (list[Message])
            The messages to use as input.

        Returns
        -------
        stream : Iterable[str] | None
            Text output stream.
        message : Message
            The Message object with metadata. (See Notes for important information.)

        Notes
        -----
        The `content` field of the returned Message object should not be to be considered fully
        populated until the Iterable is fully consumed.
        """
        raise NotImplementedError("get_completion() must be implemented in a subclass")

    def get_display_name(self) -> str:
        """
        Get the display name for the current model configuration.
        """
        model = self.get_config("model")

        if model is not None:
            return f"{self.HR_NAME} / {model}"

        return f"{self.HR_NAME}"

    def get_config(
        self,
        key: str,
        cast: Callable[[str], Any] | None = None,
        default: Any = None,
    ) -> Any:
        """
        Get a configuration value.

        Parameters
        ----------
        key : str
            The configuration key to get.
        cast : Callable[[str], Any] | None
            A function to cast the value to a different type.
        default : Any
            The default value to use if the key is not found.

        Returns
        -------
        Any
            The configuration value.
        """
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
        """
        Get a configuration dict, excluding options specified in MASKED_OPTIONS and values that are
        None.

        Returns
        -------
        dict[str, str]
           A dictionary of configuration values.
        """
        return {
            k: v
            for k, v in self.config.items()
            if
                k not in self.MASKED_OPTIONS
                and v is not None
        }

    def __repr__(self) -> str:
        args = ', '.join(
            f'{k}={repr(v)}'
            for k, v in self.__dict__.items()
            if v is not None
        )
        return f"{self.__class__.__name__}({args})"


# pylint: disable=too-few-public-methods
class ApiAdapterOption:
    """
    A class representing an API adapter option.

    Parameters
    ----------
    name: str
       The name of the option.
    hr_name: str
       The human-readable name of the option.
    description: str
       A description of the option.
    default: Any
       The default value of the option.
    default_help_override: str | None
       A string to override the default help message for this option.
    """
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

    def __repr__(self) -> str:
        args = ', '.join(
            f'{k}={repr(v)}'
            for k, v in self.__dict__.items()
            if v is not None
        )
        return f"{self.__class__.__name__}({args})"
