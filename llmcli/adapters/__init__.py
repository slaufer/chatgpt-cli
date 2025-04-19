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
    return [
        OpenAiApiAdapter,
        AnthropicApiAdapter,
        OllamaApiAdapter,
    ]


ADAPTER_INSTANCE_CACHE = {}


def get_api_adapter(name: str, params: dict) -> BaseApiAdapter:
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
