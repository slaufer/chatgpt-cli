from typing import Iterable, Tuple, Union
from llmcli.message import Message


class BaseApiAdapter:
  OPTIONS = []
  config = {}

  def __init__(self, params):
    self.config = {}

    for option in self.OPTIONS:
      if option.name in params:
        self.config[option.name] = params[option.name]
      elif option.default is not None:
        self.config[option.name] = option.default

  def get_completion(self, input_messages: list[Message]) -> Tuple[Union[Iterable[str], None], Message]:
    raise NotImplementedError('get_completion() must be implemented in a subclass')
  
  def get_display_name(self):
    model = self.config.get('model')

    if model is not None:
      return f'{self.NAME} / {model}'
    else:
      return f'{self.NAME}'


class ApiAdapterOption:
  def __init__(
      self,
      name = None,
      hr_name = None,
      description = None,
      default = None,
      default_help_override = None,
  ):
    self.name = name
    self.hr_name = hr_name
    self.description = description
    self.default = default
    self.default_help_override = default_help_override