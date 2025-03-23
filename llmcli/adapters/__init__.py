from llmcli.adapters.openai import OpenAiApiAdapter
from llmcli.adapters.anthropic import AnthropicApiAdapter
from llmcli.adapters.ollama import OllamaApiAdapter

def get_adapter_list():
  return [
    OpenAiApiAdapter,
    AnthropicApiAdapter,
    OllamaApiAdapter,
  ]

def get_api_adapter(name, params):
  for adapter in get_adapter_list():
    if adapter.NAME == name or adapter.HR_NAME == name:
      return adapter(params)

  raise Exception('No valid model adapter was selected.')