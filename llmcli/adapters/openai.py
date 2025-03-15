from openai import OpenAI
from llmcli.adapters.base import BaseModelAdapter
from llmcli.util import get_mime_type

class OpenAiModelAdapter(BaseModelAdapter):
  def __init__(
    self,
    model,
    api_key,
    max_tokens=None,
    temperature=None,
    top_p=None,
    frequency_penalty=None,
    presence_penalty=None
  ):
    self.model = model
    self.client = OpenAI(api_key=api_key)
    self.max_tokens = max_tokens
    self.temperature = temperature
    self.top_p = top_p
    self.frequency_penalty = frequency_penalty
    self.presence_penalty = presence_penalty

  def get_completion(self, input_messages):
    messages = []

    for message in input_messages:
      if message.get('role') == 'file':
        messages.append({
          "role": "user",
          "content": message.get('file_content')
        })
      elif message.get('role') == 'image':
        if self.max_tokens is None:
          self.max_tokens = 300

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
      "model": self.model,
    }

    if self.max_tokens is not None:
      req["max_tokens"] = self.max_tokens
    
    if self.temperature is not None:
      req["temperature"] = self.temperature

    if self.top_p is not None:
      req["top_p"] = self.top_p

    if self.frequency_penalty is not None:
      req["frequency_penalty"] = self.frequency_penalty

    if self.presence_penalty is not None:
      req["presence_penalty"] = self.presence_penalty

    response = self.client.chat.completions.create(**req)
    return response.choices[0].message.content