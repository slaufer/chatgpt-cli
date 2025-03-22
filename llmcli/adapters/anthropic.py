import anthropic
import os

from llmcli.adapters.base import BaseModelAdapter, ModelAdapterOption
from llmcli.util import get_mime_type


class AnthropicModelAdapter(BaseModelAdapter):
  NAME = 'anthropic'
  HR_NAME = 'Anthropic'
  OPTIONS = [
    ModelAdapterOption(name='model', hr_name='Model', description='Model ID used to generate the response.', default='claude-3-7-sonnet-latest'),
    ModelAdapterOption(name='api_key', hr_name='API Key', description='Your Anthropic API key', default=os.environ.get('ANTHROPIC_API_KEY')),
    ModelAdapterOption(name='max_tokens', hr_name='Max Tokens', description='The maximum number of tokens that can be generated in the chat completion.'),
    ModelAdapterOption(name='temperature', hr_name='Temperature', description='What sampling temperature to use, between 0 and 2.'),
    ModelAdapterOption(name='top_p', hr_name='Top P', description='An alternative to sampling with temperature, called nucleus sampling.'),
  ]
  EXTRA_HELP = "By default, uses the Anthropic API key from the environment variable ANTHROPIC_API_KEY."

  def __init__(self, param_str):
    super().__init__(param_str)
    self.client = anthropic.Anthropic(api_key=self.config.get('api_key'))

  def get_completion(self, input_messages):
    messages = []

    for message in input_messages:
      if message.get('role') == 'system':
        self.system = message.get('content')
        continue

      if message.get('role') == 'file':
        out_message = {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": message.get('file_content')
            }
          ]
        }
      elif message.get('role') == 'image':
        out_message = {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": 'IMAGE: ' + message.get('content')
            },
            {
              "type": "image",
              "source": {
                "type": "base64",
                "media_type": get_mime_type(message.get('content')),
                "data": message.get('image_content')
              }
            }
          ]
        }
      else:
        out_message = {
          "role": message.get('role'),
          "content": [
            {
              "type": "text",
              "text": message.get('content')
            }
          ]
        }

      # Merge consecutive messages of the same role (required by Anthropic API)
      if len(messages) > 0 and messages[-1].get('role') == out_message.get('role'):
        messages[-1]['content'] += out_message.get('content')
      else:
        messages.append(out_message)

    req = {}

    if self.config.get('max_tokens') is not None:
      req["max_tokens"] = self.config.get('max_tokens')

    if self.config.get('temperature') is not None:
      req["temperature"] = self.config.get('temperature')

    if self.config.get('top_p') is not None:
      req["top_p"] = self.config.get('top_p')

    if self.system is not None:
      req['system'] = self.system

    req['model'] = self.config.get('model')
    req['messages'] = messages

    response = self.client.messages.create(**req)
    return response.content[0].text