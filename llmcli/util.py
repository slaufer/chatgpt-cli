import os
import sys
import mimetypes
import argparse

from llmcli.adapters.base import BaseModelAdapter
from llmcli.adapters.openai import OpenAiModelAdapter
from llmcli.adapters.anthropic import AnthropicModelAdapter
from llmcli.adapters.ollama import OllamaModelAdapter

INTERACTIVE_KEYS = 'Press Alt+Enter to submit; Ctrl+F to add file; Ctrl+I to add image; Ctrl+S to get completion without message; Ctrl+C or Ctrl+D to exit.'

def get_model_adapter(name, params):
  """
  Get the model adapter based on the specified API and parameters.

  Args:
    name (str): The name of the model to use.
    params (dict): A dictionary of parameters, including 'api', 'max_tokens',
                   'temperature', 'top_p', 'frequency_penalty', and
                   'presence_penalty'.

  Returns:
    BaseModelAdapter: An instance of a model adapter for the specified API.

  Raises:
    Exception: If no valid model API is selected.
  """
  api = params.get('api')

  if api == 'openai':
    return OpenAiModelAdapter(
      model = name,
      api_key = os.environ.get('OPENAI_API_KEY'),
      max_tokens = params.get('max_tokens'),
      temperature = params.get('temperature'),
      top_p = params.get('top_p'),
      frequency_penalty = params.get('frequency_penalty'),
      presence_penalty = params.get('presence_penalty')
    )
  
  if api == 'anthropic':
    return AnthropicModelAdapter(
      model = name,
      api_key = os.environ.get('ANTHROPIC_API_KEY'),
      max_tokens = params.get('max_tokens'),
      temperature = params.get('temperature'),
      top_p = params.get('top_p')
    )

  if api == 'ollama':
    return OllamaModelAdapter(
      model = name
    )

  raise Exception('No valid model adapter was selected.')

def get_file(file_path):
  """
  Retrieve the content of a file.

  Args:
    file_path (str): The relative or absolute path to the file.

  Returns:
    tuple: A tuple containing the relative path of the file and its content.
  """
  path = os.path.relpath(os.path.abspath(file_path), os.getcwd())

  with open(path, 'r') as file:
    content = file.read()

  return path, content

def get_mime_type(image_path):
  """
  Determine the MIME type of a file based on its file extension.

  Args:
    image_path (str): The path to the image file.

  Returns:
    str: The MIME type of the file. Defaults to 'image/jpeg' if unknown.
  """
  mime_type, _ = mimetypes.guess_type(image_path)

  if mime_type is None:
    return 'image/jpeg'
  
  return mime_type

def get_args():
  parser = argparse.ArgumentParser(
    description='ChatGPT CLI',
    add_help=False,
  )

  # Message arguments
  # Argparse is just validating these, we parse them manually below
  parser.add_argument('-s', '--system', action='append')
  parser.add_argument('-a', '--assistant', action='append')
  parser.add_argument('-u', '--user', action='append')
  parser.add_argument('-f', '--file', action='append')
  parser.add_argument('-i', '--image', action='append')
  parser.add_argument('-c', '--conversation', action='append')
  parser.add_argument('-d', '--no-system-prompt', action='store_true')

  # Model arguments
  parser.add_argument('-p', '--api', choices=['openai', 'anthropic', 'ollama'], default='openai')
  parser.add_argument('--temperature', type=float)
  parser.add_argument('--max-tokens', type=int)
  parser.add_argument('--top-p', type=float)
  parser.add_argument('--frequency-penalty', type=float)
  parser.add_argument('--presence-penalty', type=float)

  # Other arguments
  parser.add_argument('-n', '--non-interactive', action='store_true')
  parser.add_argument('-l', '--log-file')
  parser.add_argument('-j', '--log-file-json')
  parser.add_argument('-m', '--model', default='gpt-4o')
  parser.add_argument('-g', '--immediate', action='store_true')
  parser.add_argument('-x', '--separator')
  parser.add_argument('-o', '--no-intro', action='store_true')
  parser.add_argument('-h', '--help', action='store_true')

  return parser.parse_args()

def print_help():
  exec_path = os.path.basename(sys.argv[0])
  print(f"""
LLM CLI

This command line interface allows you to interact with OpenAI and Anthropic's chat completion APIs in various ways, including sending system prompts, assistant responses, user prompts, and loading previous conversations. It supports both interactive and non-interactive modes.

Usage:
  {exec_path} [options]

Options:
  MESSAGE ARGUMENTS:
  -s, --system <message>       Add a system prompt message. If not specified, a default system prompt is used.
  -a, --assistant <message>    Add an assistant response message.
  -u, --user <message>         Add a user prompt message.
  -f, --file <filename>        Add a user prompt message from a file.
  -i, --image <filename>       Add a user prompt message from an image. If --max-tokens is not specified, a default value may be applied.
  -c, --conversation <file>    Load a previous conversation from a file. (see -j / --log-file-json)
  -d, --no-system-prompt       Don't add a default system prompt if none is present.
  
  MODEL ARGUMENTS:
  -m, --model <model_name>     Specify the model to use. (default: gpt-4o)
  -p, --api                        Specify the API to use. Required for unrecognized models. (options: openai, anthropic, ollama; default: openai)
  --temperature <value>        The sampling temperature to use, between 0 and 1.
  --max-tokens <number>        The maximum number of tokens to generate in the completion.
  --top-p <value>              The top-p sampling value to use, between 0 and 1.
  --frequency-penalty <value>  The frequency penalty to use, between -2.0 and 2.0. (OpenAI models only)
  --presence-penalty <value>   The presence penalty to use, between -2.0 and 2.0. (OpenAI models only)
        
  OTHER ARGUMENTS:
  -n, --non-interactive        Disable interactive mode, get a completion and exit. Use message arguments to specify the conversation.
  -l, --log-file <filename>    Log output to a specified file.
  -j, --log-file-json <file>   Output a JSON-formatted log to a specified file.
  -g, --immediate              Get an assistant response immediately, before entering interactive mode.
  -x, --separator <separator>  Specify the separator to use between messages.
  -o, --no-intro               Don't print the system prompt, or messages specified on the command line.
  -h, --help                   Print this help message and exit.

Message arguments are added to the conversation in the order in which they are specified on the command line. If no system prompt is specified, a default prompt will be added.

By default, the program begins in interactive mode. Interactive mode uses a multi-line editor. {INTERACTIVE_KEYS}

Make sure you set the appropriate API key environment variable. For OpenAI models, set OPENAI_API_KEY. For Anthropic models, set ANTHROPIC_API_KEY.

TIP: Try `{exec_path} -c mylog.json -j mylog.json` to persist conversations between sessions.
        """.strip())
