import os
import sys
import json
import base64

from shutil import get_terminal_size

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from llmcli.util import get_args
from llmcli.help import print_help, INTERACTIVE_KEYS

from llmcli.adapters import get_model_adapter

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
    model_adapter=None
  ):
    self.log_file = log_file
    self.json_log_file = log_file_json
    self.interactive = interactive
    self.immediate = immediate
    self.separator = separator
    self.intro = intro
    self.no_system_prompt = no_system_prompt
    self.model_adapter = model_adapter
    self.messages = []

  def log_json(self):
      """Dump the messages to a JSON file."""
      if self.json_log_file:
        with open(self.json_log_file, 'w') as file:
            json.dump(self.messages, file, indent=4)

  def output(self, message, silent=False):
    if not silent:
      print(message, end='', flush=True)

    if self.log_file is not None:
      with open(self.log_file, 'a') as file:
        file.write(message)

  def get_completion(self):
    return self.model_adapter.get_completion(self.messages)

  def get_separator(self):
    if self.separator is not None:
      return self.separator
    
    return '\n\n #' + ('=' * (get_terminal_size().columns - 4)) + '#\n\n'

  def add_chat_message(self, role, content, message=None, silent=False):
    if role == 'file':
      if message and 'file_content' in message:
        content = message.get('content')
        file_content = message.get('file_content')
      else:
        file_path = os.path.relpath(os.path.abspath(content), os.getcwd())
        content = file_path
        with open(file_path, 'r') as file:
          file_content = '### FILE: `{file_path}`\n```\n' + file.read() + '\n```'

      message = {
        "role": "file",
        "content": content,
        "file_content": file_content
      }
      self.messages.append(message)
      self.output('FILE: ' + message.get('content') + ' (contents hidden)', silent=silent)
    elif role == 'image':
      if message and 'image_content' in message:
        content = message.get('content')
        image_content = message.get('image_content')
      else:
        file_path = os.path.relpath(os.path.abspath(content), os.getcwd())
        content = file_path
        with open(file_path, 'rb') as file:
          image_content = base64.b64encode(file.read()).decode('utf-8')
      message = {
        "role": "image",
        "content": content,
        "image_content": image_content
      }
      self.messages.append(message)
      self.output('IMAGE: ' + message.get('content') + ' (contents hidden)', silent=silent)
    else:
      self.messages.append({"role": role, "content": content})
      self.output(f'{role.capitalize()}:\n\n{content}', silent=silent)
    
    self.output(self.get_separator(), silent=silent)

  def add_messages_from_args(self, args):
    silent = not self.interactive or not self.intro

    args_iter = iter(args)
    args_messages = []

    for arg in args_iter:
      if arg not in ('-s', '--system', '-a', '--assistant', '-u', '--user', '-f', '--file', '-i', '--image', '-c', '--conversation'):
        continue

      content = next(args_iter, None)

      if arg in ('-s', '--system'):
        args_messages.append({"role": "system", "content": content})
      elif arg in ('-a', '--assistant'):
        args_messages.append({"role": "assistant", "content": content})
      elif arg in ('-u', '--user'):
        args_messages.append({"role": "user", "content": content})
      elif arg in ('-f', '--file'):
        args_messages.append({"role": "file", "content": content})
      elif arg in ('-i', '--image'):
        args_messages.append({"role": "image", "content": content})
      elif arg in ('-c', '--conversation'):
        # so you can combine -c and -j on a file that doesn't exist yet
        if not os.path.exists(content) and self.json_log_file == content:
          continue

        with open(content, 'r') as file:
          conversation = json.load(file)
          for message in conversation:
            args_messages.append(message)

    if not self.no_system_prompt and not any(message.get("role") == "system" for message in args_messages):
      args_messages.insert(0, {"role": "system", "content": DEFAULT_SYSTEM_PROMPT})

    for message in args_messages:
      self.add_chat_message(message.get('role'), message.get('content'), message=message, silent=silent)

  def menu(self):
    self.output('llmcli menu:\n')
    self.output('[1] Add a file\n')
    self.output('[2] Add an image\n')
    self.output('[3] Get completion\n')
    self.output('[4] Change API\n')
    self.output('[5] Change API options\n')
    self.output('[6] Change JSON log file\n')
    self.output('[7] Import JSON log file\n')
    self.output('[8] Exit menu\n')
    self.output('\nEnter selection: ')
    choice = prompt()

    self.output("You chose: "  + choice + "\n")

  def main(self, args):
    if self.interactive:
        self.output(f'{INTERACTIVE_KEYS}' + self.get_separator())

    self.add_messages_from_args(args)

    if not self.interactive:
      response = self.get_completion()
      self.add_chat_message("assistant", response, silent=True)
      self.log_json()
      self.output(response)
      return
    
    if self.immediate:
      response = self.get_completion()
      self.add_chat_message("assistant", response)

    self.log_json()

    bindings = KeyBindings()
    bindings.add('c-c')(lambda _: sys.exit(0))
    bindings.add('c-d')(lambda _: sys.exit(0))
    bindings.add('enter')(lambda event: event.app.current_buffer.insert_text('\n'))
    bindings.add('escape', 'enter')(lambda event: event.app.exit(result=(event.app.current_buffer.text, 'text')))
    bindings.add('c-m')(lambda event: event.app.exit(result=(None, 'menu')))
    bindings.add('c-s')(lambda event: event.app.exit(result=(None, 'skip')))
    bindings.add('c-i')(lambda event: event.app.exit(result=(event.app.current_buffer.text, 'image')))
    bindings.add('c-f')(lambda event: event.app.exit(result=(event.app.current_buffer.text, 'file')))

    while True:
      self.output("User:\n\n")
      (user_input, user_input_type) = prompt('', multiline=True, key_bindings=bindings)

      try:
        if user_input_type == 'skip':
          pass
        elif user_input_type == 'text':
          self.add_chat_message('user', user_input, silent=True)
        elif user_input_type == 'file':
          self.add_chat_message('file', user_input)
        elif user_input_type == 'image':
          self.add_chat_message('image', user_input)
        elif user_input_type == 'menu':
          self.menu()
          continue
      except Exception as e:
        self.output(f'Unable to add message: {str(e)}\n\n')
        continue

      self.log_json()


      if user_input_type in ['text', 'skip']:
        self.output(self.get_separator())

        try:
          response = self.get_completion()
          self.add_chat_message("assistant", response)
        except Exception as e:
          self.output(f'Unable to get completion: {str(e)}\n\n')
          continue

        self.log_json()

###############
# INITIALIZER #
###############

def main():
  args = get_args()

  if args.help:
    print_help()
    return

  if (os.environ.get("OPENAI_API_KEY") is None):
    print("Please set the OPENAI_API_KEY environment variable to your OpenAI API key. Use -h for help.")
    sys.exit(1)

  cli = LlmCli(
    log_file=args.log_file,
    log_file_json=args.log_file_json,
    interactive=not args.non_interactive,
    immediate=args.immediate,
    separator=args.separator,
    intro=not args.no_intro,
    no_system_prompt=args.no_system_prompt,
    model_adapter=get_model_adapter(args.api, args.api_options)
  )

  cli.main(sys.argv[1:])
