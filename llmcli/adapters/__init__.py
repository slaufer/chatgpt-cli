"""
Contains general functions related to API adapters.
"""
import json

from llmcli.adapters.base import BaseApiAdapter
from llmcli.adapters.openai import OpenAiApiAdapter
from llmcli.adapters.anthropic import AnthropicApiAdapter
from llmcli.adapters.ollama import OllamaApiAdapter

__all__ = [
    "BaseApiAdapter",
    "OpenAiApiAdapter",
    "AnthropicApiAdapter",
    "OllamaApiAdapter",
]

def get_adapter_list() -> list[BaseApiAdapter]:
    """
    Get a list of available API adapters.

    Returns
    -------
    list[BaseApiAdapter]
        A list of available API adapters.
    """
    return [
        OpenAiApiAdapter,
        AnthropicApiAdapter,
        OllamaApiAdapter,
    ]

def parse_api_params(params: list[str]) -> dict:
    """
    Parse a list of API parameters into a dictionary for API adapter constructors.

    Parameters
    ----------
    params : list of str
        A list of strings in the format "key=value".

    Returns
    -------
    dict
        A dictionary where keys are parameter names and values are parameter values.
        Returns an empty dictionary if `params` is None.
    """
    if params is None:
        return {}

    return {
        k: v for [k, v] in
        [
            [s.strip() for s in param.split("=", maxsplit=1)]
            for param in params
            if "=" in param
        ]
    }

ADAPTER_INSTANCE_CACHE = {}

def get_api_adapter(name: str, params: dict) -> BaseApiAdapter:
    """
    Get an API adapter instance by identifier, with the provided parameters. May return a cached
    instance.

    Parameters
    ----------
    name : str
        The identifier of the API adapter to use.
    params : dict
        Parameters for the API adapter.

    Returns
    -------
    BaseApiAdapter
        An instance of the API adapter.

    Raises
    ------
    Exception
        If no valid adapter is selected.
    """
    params_str = json.dumps(params, sort_keys=True)
    adapter_instance = ADAPTER_INSTANCE_CACHE.get((name, params_str))

    if adapter_instance is not None:
        return adapter_instance

    for adapter in get_adapter_list():
        if name in (adapter.NAME, adapter.HR_NAME):
            adapter_instance = adapter(params)
            ADAPTER_INSTANCE_CACHE[(name, params_str)] = adapter_instance
            return adapter_instance

    raise Exception("No valid adapter was selected.")
