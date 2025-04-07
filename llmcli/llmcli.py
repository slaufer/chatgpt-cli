import os
import sys
import json
import base64

from shutil import get_terminal_size
from typing import Iterable

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from llmcli.util import get_args, parse_api_params_str
from llmcli.help import print_help, INTERACTIVE_KEYS
from llmcli.adapters import get_api_adapter
from llmcli.message import Message

DEFAULT_SYSTEM_PROMPT = f'''
Carefully heed the user's instructions.
Respond using Markdown.
Respond briefly and concisely unless you are instructed to do otherwise.
Do not include any extraneous or tangential details unless you are instructed to do otherwise.
'''.strip()


class LlmCli:
  def __init__(
    self,
    log_file=None,
    log_file_json=None,
    interactive=True,
    immediate=False,
    separator = None,
    intro=True,
    no_system_prompt=False,
    api_adapter_name=None,
    api_adapter_options=None,
  ):
    self.log_file = log_file
    self.json_log_file = log_file_json
    self.interactive = interactive
    self.immediate = immediate
    self.separator = separator
    self.intro = intro
    self.no_system_prompt = no_system_prompt

    self.api_adapter_name = api_adapter_name
    self.api_adapter_options = api_adapter_options
    self.api_adapter = get_api_adapter(self.api_adapter_name, parse_api_params_str(self.api_adapter_options))

    self.messages = []

  @staticmethod
  def encode(obj):
    if isinstance(obj, Message):
      return obj.to_dict()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

  def log_json(self):
    if self.json_log_file:
      with open(self.json_log_file, 'w') as file:
          json.dump(self.messages, file, indent=4, default=self.encode)

  def get_completion(self):
    return self.api_adapter.get_completion(self.messages)

  def get_separator(self):
    if self.separator is not None:
      return self.separator

    return '\n #' + ('=' * (get_terminal_size().columns - 4)) + '#\n'

  def add_chat_message(self, stream: Iterable[str] = None, message: Message = Message(), silent: bool=False):
    if not silent:
      print(f'{message.display_name}:\n')

      # if there is a stream, we have to sink the entire thing before we can be sure the Message is complete
      if (stream is not None):
        for chunk in stream:
          print(chunk, end='')
      else:
        print(message.content)

      print('\n' + self.get_separator())

    self.messages.append(message)

  def add_messages_from_args(self, args):
    silent = not self.interactive or not self.intro

    args_iter = iter(args)
    args_messages = []

    for arg in args_iter:
      if arg not in ('-s', '--system', '-a', '--assistant', '-u', '--user', '-f', '--file', '-i', '--image', '-c', '--conversation'):
        continue

      arg_value = next(args_iter, None)

      if arg in ('-s', '--system'):
        args_messages.append(Message(role="system", content=arg_value))
      elif arg in ('-a', '--assistant'):
        args_messages.append(Message(role="assistant", content=arg_value))
      elif arg in ('-u', '--user'):
        args_messages.append(Message(role="user", content=arg_value))
      elif arg in ('-f', '--file'):
        args_messages.append(Message(role="user", file_path=arg_value))
      elif arg in ('-i', '--image'):
        args_messages.append(Message(role="user", image_path=arg_value))
      elif arg in ('-c', '--conversation'):
        # so you can combine -c and -j on a file that doesn't exist yet
        if not os.path.exists(arg_value) and self.json_log_file == arg_value:
          continue

        with open(arg_value, 'r') as file:
          conversation = json.load(file)
          for message in conversation:
            args_messages.append(Message.from_dict(message))

    if not self.no_system_prompt and not any(message.role == "system" for message in args_messages):
      args_messages.insert(0, Message(role="system", content=DEFAULT_SYSTEM_PROMPT))

    for message in args_messages:
      self.add_chat_message(message=message, silent=silent)

  def add_file(self):
    input = prompt('Enter file path: ')
    self.add_chat_message(message=Message(role="user", file_path=os.path.expanduser(input)))
  
  def add_image(self):
    input = prompt('Enter image path: ')
    self.add_chat_message(message=Message(role="user", image_path=os.path.expanduser(input)))

  def change_api_adapter_name(self):
    api_adapter_name = prompt('Enter API name: ', default=self.api_adapter_name)
    api_adapter = get_api_adapter(api_adapter_name, parse_api_params_str(self.api_adapter_options))
    self.api_adapter_name = api_adapter_name
    self.api_adapter = api_adapter

  def change_api_adapter_options(self):
    api_adapter_options = prompt('Enter API options: ', default=self.api_adapter_options)
    api_adapter = get_api_adapter(self.api_adapter_name, parse_api_params_str(api_adapter_options))
    self.api_adapter_options = api_adapter_options
    self.api_adapter = api_adapter

  def change_json_log_file(self):
    json_log_file = prompt('Enter JSON log file path: ')

    if json_log_file.strip() == '':
      json_log_file = None
    else:
      self.json_log_file = os.path.expanduser(json_log_file)

    self.log_json()

  def menu(self):
    opts = [
      ('Add a file', lambda: self.add_file()),
      ('Add an image', lambda: self.add_image()),
      ('Change API', lambda: self.change_api_adapter_name()),
      ('Change API options', lambda: self.change_api_adapter_options()),
      ('Change JSON log file', lambda: self.change_json_log_file()),
      ('Exit menu', lambda: None),
      ('Quit', lambda: sys.exit(0)),
    ]

    for i, opt in enumerate(opts):
      print(f'[{i}] {opt[0]}')

    input = prompt('\nEnter selection: ')

    try:
      choice = int(input)
    except ValueError:
      print(f'Invalid selection: {input}')
      return
    
    if choice < 0 or choice >= len(opts):
      print(f'Invalid selection: {choice}')
      return

    try:
      opts[choice][1]()
    except Exception as e:
      print(f'Error: {e}')

  def repl(self, bindings):
    default_input = None

    while True:
      print("User:\n")
      (user_input, user_input_type) = prompt(multiline=True, key_bindings=bindings, default=default_input or '')
      default_input = None

      try:
        if user_input_type == 'text':
          self.add_chat_message(message=Message(role="user", content=user_input), silent=True)
        elif user_input_type == 'menu':
          self.menu()
          default_input = user_input
          continue
      except Exception as e:
        print(f'Unable to add message: {str(e)}\n')
        continue

      self.log_json()

      if user_input_type == 'text':
        print(self.get_separator())

        try:
          response_stream, response_message = self.get_completion()
          self.add_chat_message(stream = response_stream, message=response_message)
        except Exception as e:
          print(f'Unable to get completion: {str(e)}\n')
          continue

        self.log_json()

  def main(self, args):
    if self.interactive:
        print(f'{INTERACTIVE_KEYS}' + self.get_separator())

    self.add_messages_from_args(args)

    if not self.interactive:
      response_stream, response_message = self.get_completion()
      for fragment in response_stream:
          print(fragment, end='')
      self.add_chat_message(stream=response_stream, message=response_message, silent=True)
      self.log_json()
      return
    
    if self.immediate:
      response_stream, response_message = self.get_completion()
      self.add_chat_message(stream=response_stream, message=response_message)

    self.log_json()

    bindings = KeyBindings()
    bindings.add('c-c')(lambda _: sys.exit(0))
    bindings.add('c-d')(lambda _: sys.exit(0))
    bindings.add('enter')(lambda event: event.app.current_buffer.insert_text('\n'))
    bindings.add('escape', 'enter')(lambda event: event.app.exit(result=(event.app.current_buffer.text, 'text')))
    bindings.add('c-b')(lambda event: event.app.exit(result=(event.app.current_buffer.text, 'menu')))

    self.repl(bindings)

###############
# INITIALIZER #
###############

def main():
  args = get_args()

  if args.help:
    print_help()
    return

  cli = LlmCli(
    log_file=args.log_file,
    log_file_json=args.log_file_json,
    interactive=not args.non_interactive,
    immediate=args.immediate,
    separator=args.separator,
    intro=not args.no_intro,
    no_system_prompt=args.no_system_prompt,
    api_adapter_name=args.api,
    api_adapter_options=args.api_options,
  )

  cli.main(sys.argv[1:])
