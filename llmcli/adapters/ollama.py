import ollama

from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption


class OllamaApiAdapter(BaseApiAdapter):
  NAME = 'ollama'
  HR_NAME = 'Ollama'
  OPTIONS = [
    ApiAdapterOption(name='model', hr_name='Model', description='Model ID used to generate the response.', default='llama3.1:8b'),
  ]
  EXTRA_HELP = "By default, uses an Ollama instance running on localhost. For remote instances, set the OLLAMA_HOST environment variable."

  def __init__(self, params):
    super().__init__(params)

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