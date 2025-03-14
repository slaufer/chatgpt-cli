import ollama

from llmcli.adapters.base import BaseModelAdapter

import asyncio

class OllamaModelAdapter(BaseModelAdapter):
  def __init__(self, model):
    self.model = model

  def get_completion(self, input_messages):
    messages = []

    for message in input_messages:
      if message.get('role') == 'file':
        messages.append({
          "role": "user",
          "content": message.get('file_content')
        })
      elif message.get('role') == 'image':
        # TODO
        pass
      else:
        messages.append(message)

    response = ollama.chat(model=self.model, messages=messages)
    return response.message.content