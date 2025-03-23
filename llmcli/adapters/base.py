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

  def get_completion(messages):
    raise NotImplementedError('get_completion() must be implemented in a subclass')

class ApiAdapterOption:
  def __init__(
      self,
      name = None,
      hr_name = None,
      description = None,
      default = None
  ):
    self.name = name
    self.hr_name = hr_name
    self.description = description
    self.default = default