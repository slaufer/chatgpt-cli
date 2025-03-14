import anthropic

from llmcli.adapters.base import BaseModelAdapter

class AnthropicModelAdapter(BaseModelAdapter):
  def __init__(
    self,
    model,
    api_key,
    max_tokens=None,
    temperature=None,
    top_p=None
  ):
    self.system = ""
    self.model = model
    self.client = anthropic.Anthropic(api_key=api_key)
    self.max_tokens = max_tokens
    self.temperature = temperature
    self.top_p = top_p

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

    if self.temperature is not None:
      req['temperature'] = self.temperature

    if self.max_tokens is not None:
      req['max_tokens'] = self.max_tokens
    else:
      req['max_tokens'] = 300

    if self.top_p is not None:
      req['top_p'] = self.top_p

    if self.system is not None:
      req['system'] = self.system

    req['model'] = self.model
    req['messages'] = messages

    response = self.client.messages.create(**req)
    return response.content[0].text