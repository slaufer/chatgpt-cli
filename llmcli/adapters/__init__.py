from llmcli.adapters.openai import OpenAiModelAdapter
from llmcli.adapters.anthropic import AnthropicModelAdapter
from llmcli.adapters.ollama import OllamaModelAdapter

def get_adapter_list():
  return [
    OpenAiModelAdapter,
    AnthropicModelAdapter,
    OllamaModelAdapter,
  ]

def get_model_adapter(name, params):
  for adapter in get_adapter_list():
    if adapter.NAME == name or adapter.HR_NAME == name:
      return adapter(params)

  raise Exception('No valid model adapter was selected.')