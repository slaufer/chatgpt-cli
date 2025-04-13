from typing import Iterable, Tuple, Union
import ollama

from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption
from llmcli.message import Message


class OllamaApiAdapter(BaseApiAdapter):
  NAME = 'ollama'
  HR_NAME = 'Ollama'
  OPTIONS = [
    ApiAdapterOption(name='model', hr_name='Model', description='Model ID used to generate the response.', default='llama3.1:8b'),
    ApiAdapterOption(name='mirostat', hr_name='Mirostat', description='Enable Mirostat sampling for controlling perplexity.'),
    ApiAdapterOption(name='mirostat_eta', hr_name='Mirostat Eta', description='Influences how quickly the algorithm responds to feedback from the generated text.'),
    ApiAdapterOption(name='mirostat_tau', hr_name='Mirostat Tau', description='Controls the balance between coherence and diversity of the output.'),
    ApiAdapterOption(name='num_ctx', hr_name='Context Size', description='Sets the size of the context window used to generate the next token.'),
    ApiAdapterOption(name='repeat_last_n', hr_name='Repeat Last N', description='Sets how far back for the model to look back to prevent repetition.'),
    ApiAdapterOption(name='repeat_penalty', hr_name='Repeat Penalty', description='Sets how strongly to penalize repetitions.'),
    ApiAdapterOption(name='temperature', hr_name='Temperature', description='The temperature of the model; higher values increase creativity.'),
    ApiAdapterOption(name='seed', hr_name='Seed', description='Sets the random number seed to use for generation.'),
    ApiAdapterOption(name='stop', hr_name='Stop Sequence', description='Sets the stop sequences to use; generation stops when encountered.'),
    ApiAdapterOption(name='num_predict', hr_name='Max Tokens', description='Maximum number of tokens to predict when generating text.'),
    ApiAdapterOption(name='top_k', hr_name='Top-K', description='Reduces the probability of generating nonsense by limiting token selection.'),
    ApiAdapterOption(name='top_p', hr_name='Top-P', description='Controls diversity via nucleus sampling; higher values yield more diverse text.'),
    ApiAdapterOption(name='min_p', hr_name='Min-P', description='Ensures a minimum probability threshold for token selection.'),    
  ]
  EXTRA_HELP = "By default, uses an Ollama instance running on localhost. For remote instances, set the OLLAMA_HOST environment variable."

  def __init__(self, params) -> None:
    super().__init__(params)

  @staticmethod
  def output_stream(response_stream: Iterable[dict], response_message: Message) -> Iterable[str]:
    for chunk in response_stream:
      fragment = chunk['message']['content']
      response_message.content += fragment
      yield fragment

  def get_completion(self, input_messages: list[Message]) -> Tuple[Union[Iterable[str], None], Message]:
    messages = []

    for message in input_messages:
      if message.file_content is not None:
        messages.append({
          "role": message.role,
          "content": f'### FILE: {message.file_path}\n\n```\n{message.file_content}\n```'
        })
      elif message.image_content is not None:
        messages.append({
          "role": message.role,
          "content": f'### IMAGE: {message.image_path}',
          "images": [message.image_content]
        })
      else:
        messages.append({
          "role": message.role,
          "content": message.content
        })

    options = ollama.Options()

    if self.config.get('mirostat') is not None:
      options.mirostat = int(self.config.get('mirostat'))

    if self.config.get('mirostat_eta') is not None:
      options.mirostat_eta = float(self.config.get('mirostat_eta'))

    if self.config.get('mirostat_tau') is not None:
      options.mirostat_tau = float(self.config.get('mirostat_tau'))

    if self.config.get('num_ctx') is not None:
      options.num_ctx = int(self.config.get('num_ctx'))

    if self.config.get('repeat_last_n') is not None:
      options.repeat_last_n = int(self.config.get('repeat_last_n'))

    if self.config.get('repeat_penalty') is not None:
      options.repeat_penalty = float(self.config.get('repeat_penalty'))

    if self.config.get('temperature') is not None:
      options.temperature = float(self.config.get('temperature'))

    if self.config.get('seed') is not None:
      options.seed = int(self.config.get('seed'))

    if self.config.get('stop') is not None:
      options.stop = str(self.config.get('stop'))

    if self.config.get('num_predict') is not None:
      options.num_predict = int(self.config.get('num_predict'))

    if self.config.get('top_k') is not None:
      options.top_k = int(self.config.get('top_k'))

    if self.config.get('top_p') is not None:
      options.top_p = float(self.config.get('top_p'))

    if self.config.get('min_p') is not None:
      options.min_p = float(self.config.get('min_p'))

    response_stream = ollama.chat(
      model=self.config.get('model'),
      messages=messages,
      options=options,
      stream=True
    )

    response_message = Message(
      role="assistant",
      content='',
      adapter=self.NAME,
      adapter_options=self.config,
      display_name=self.get_display_name(),
    )

    return self.output_stream(response_stream, response_message), response_message