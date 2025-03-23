import os

from openai import OpenAI
from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption
from llmcli.util import get_mime_type


class OpenAiApiAdapter(BaseApiAdapter):
  NAME = 'openai'
  HR_NAME='OpenAI'
  OPTIONS = [
    ApiAdapterOption(name='model', hr_name='Model', description='Model ID used to generate the response.', default='gpt-4o'),
    ApiAdapterOption(name='api_key', hr_name='API Key', description='Your OpenAI API key', default=os.environ.get('OPENAI_API_KEY')),
    ApiAdapterOption(name='max_tokens', hr_name='Max Tokens', description='The maximum number of tokens that can be generated in the chat completion.'),
    ApiAdapterOption(name='temperature', hr_name='Temperature', description='What sampling temperature to use, between 0 and 2.'),
    ApiAdapterOption(name='top_p', hr_name='Top P', description='An alternative to sampling with temperature, called nucleus sampling.'),
    ApiAdapterOption(name='frequency_penalty', hr_name='Frequency Penalty', description='Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far.'),
    ApiAdapterOption(name='presence_penalty', hr_name='Presence Penalty', description='Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far.')
  ]
  EXTRA_HELP = "By default, uses the OpenAI API key from the environment variable OPENAI_API_KEY."

  def __init__(self, params):
    super().__init__(params)
    self.client = OpenAI(api_key=self.config.get('api_key'))

  def get_completion(self, input_messages):
    messages = []

    for message in input_messages:
      if message.get('role') == 'file':
        messages.append({
          "role": "user",
          "content": message.get('file_content')
        })
      elif message.get('role') == 'image':
        if self.config.get('max_tokens') is None:
          self.config['max_tokens'] = 300

        messages.append({
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": 'IMAGE: ' + message.get('content')
            },
            {
              "type": "image_url",
              "image_url": {
                "url": 'data:' + get_mime_type(message.get('content')) + ';base64,' + message.get('image_content')
              }
            }
          ]
        })
      else:
        messages.append(message)

    req = {
      "messages": messages,
      "model": self.config.get('model'),
    }

    if self.config.get('max_tokens') is not None:
      req["max_tokens"] = self.config.get('max_tokens')

    if self.config.get('temperature') is not None:
      req["temperature"] = self.config.get('temperature')

    if self.config.get('top_p') is not None:
      req["top_p"] = self.config.get('top_p')

    if self.config.get('frequency_penalty') is not None:
      req["frequency_penalty"] = self.config.get('frequency_penalty')

    if self.config.get('presence_penalty') is not None:
      req["presence_penalty"] = self.config.get('presence_penalty')

    response = self.client.chat.completions.create(**req)
    return response.choices[0].message.content