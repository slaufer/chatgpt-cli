from typing import Iterable, Tuple, Union
import anthropic
import os

from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption
from llmcli.message import Message


class AnthropicApiAdapter(BaseApiAdapter):
  NAME = 'anthropic'
  HR_NAME = 'Anthropic'
  OPTIONS = [
    ApiAdapterOption(name='model', hr_name='Model', description='Model ID used to generate the response.', default='claude-3-7-sonnet-latest'),
    ApiAdapterOption(name='api_key', hr_name='API Key', description='Your Anthropic API key', default=os.environ.get('ANTHROPIC_API_KEY'), default_help_override='ANTHROPIC_API_KEY'),
    ApiAdapterOption(name='max_tokens', hr_name='Max Tokens', description='The maximum number of tokens that can be generated in the chat completion', default=1000),
    ApiAdapterOption(name='temperature', hr_name='Temperature', description='What sampling temperature to use, between 0 and 2.'),
    ApiAdapterOption(name='top_p', hr_name='Top P', description='An alternative to sampling with temperature, called nucleus sampling.'),
  ]
  EXTRA_HELP = "By default, uses the Anthropic API key from the environment variable ANTHROPIC_API_KEY."

  def __init__(self, params):
    super().__init__(params)
    self.client = anthropic.Anthropic(api_key=self.config.get('api_key'))

  @staticmethod
  def output_stream(response_stream: anthropic.Stream, response_message: Message) -> Iterable[str]:
    for chunk in response_stream:
      if chunk.type != 'content_block_delta' or chunk.delta.type != 'text_delta':
        continue

      fragment = chunk.delta.text
      response_message.content += fragment
      yield fragment

  def get_completion(self, input_messages: list[Message]) -> Tuple[Union[Iterable[str], None], Message]:
    messages = []

    for message in input_messages:
      if message.role == 'system':
        self.system = message.content
        continue

      if message.file_content is not None:
        out_message = {
          "role": message.role,
          "content": [
            {
              "type": "text",
              "text": f'### FILE: {message.file_path}\n\n```\n{message.file_content}\n```',
            }
          ]
        }
      elif message.image_content is not None:
        out_message = {
          "role": message.role,
          "content": [
            {
              "type": "text",
              "text": f'### IMAGE: {message.image_path}',
            },
            {
              "type": "image",
              "source": {
                "type": "base64",
                "media_type": message.image_type,
                "data": message.image_content,
              }
            }
          ]
        }
      else:
        out_message = {
          "role": message.role,
          "content": [
            {
              "type": "text",
              "text": message.content
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
      req["max_tokens"] = int(self.config.get('max_tokens'))

    if self.config.get('temperature') is not None:
      req["temperature"] = float(self.config.get('temperature'))

    if self.config.get('top_p') is not None:
      req["top_p"] = float(self.config.get('top_p'))

    if self.system is not None:
      req['system'] = self.system

    req['model'] = self.config.get('model')
    req['messages'] = messages
    req['stream'] = True

    response_stream = self.client.messages.create(**req)
    
    response_message = Message(
      role="assistant",
      content='',
      adapter=self.NAME,
      adapter_options=self.config,
      display_name=self.get_display_name(),
    )

    return self.output_stream(response_stream, response_message), response_message