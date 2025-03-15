import os

from llmcli.adapters.base import BaseModelAdapter
from llmcli.adapters.openai import OpenAiModelAdapter
from llmcli.adapters.anthropic import AnthropicModelAdapter
from llmcli.adapters.ollama import OllamaModelAdapter

def get_model_adapter(name, params):
  """
  Get the model adapter based on the specified API and parameters.

  Args:
    name (str): The name of the model to use.
    params (dict): A dictionary of parameters, including 'api', 'max_tokens',
                   'temperature', 'top_p', 'frequency_penalty', and
                   'presence_penalty'.

  Returns:
    BaseModelAdapter: An instance of a model adapter for the specified API.

  Raises:
    Exception: If no valid model API is selected.
  """
  api = params.get('api')

  if api == 'openai':
    return OpenAiModelAdapter(
      model = name,
      api_key = os.environ.get('OPENAI_API_KEY'),
      max_tokens = params.get('max_tokens'),
      temperature = params.get('temperature'),
      top_p = params.get('top_p'),
      frequency_penalty = params.get('frequency_penalty'),
      presence_penalty = params.get('presence_penalty')
    )
  
  if api == 'anthropic':
    return AnthropicModelAdapter(
      model = name,
      api_key = os.environ.get('ANTHROPIC_API_KEY'),
      max_tokens = params.get('max_tokens'),
      temperature = params.get('temperature'),
      top_p = params.get('top_p')
    )

  if api == 'ollama':
    return OllamaModelAdapter(
      model = name
    )

  raise Exception('No valid model adapter was selected.')