import os
import sys

from llmcli.adapters import get_adapter_list

INTERACTIVE_KEYS = 'Press Alt+Enter to submit; Ctrl+M to show the menu; Ctrl+C or Ctrl+D to exit.'

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

  Message arguments are added to the conversation in the order in which they are specified on the command line.

  API ARGUMENTS:
  -p, --api <identifier>       Identifier of the API adapter to use. (See ADAPTERS below.) (default: openai)
  -o, --api-options <options>  API option, in the format key=value. May be used multiple times.  (See ADAPTERS below.)

  See ADAPTERS below for a list of API identifiers.

  OTHER ARGUMENTS:
  -n, --non-interactive        Disable interactive mode, get a completion and exit. Use message arguments to specify the conversation.
  -j, --log-file-json <file>   Output a JSON-formatted log to a specified file.
  -g, --immediate              Get an assistant response immediately, before entering interactive mode.
  -x, --separator <separator>  Specify the separator to use between messages.
  -q, --no-intro               Don't print the system prompt, or messages specified on the command line.
  -h, --help                   Print this help message and exit.

  By default, the program begins in interactive mode. Interactive mode uses a multi-line editor. {INTERACTIVE_KEYS}

  TIP: Try `{exec_path} -c mylog.json -j mylog.json` to persist conversations between sessions.

  ADAPTERS:
""".strip())
  
  for adapter in get_adapter_list():
    print(f"    {adapter.HR_NAME} ({adapter.NAME})")
    print(f"      OPTIONS:")

    for option in adapter.OPTIONS:
      if option.default_help_override is not None:
        print(f"      - {option.name : <22} {option.description} (default: {option.default_help_override})")
      elif option.default is not None:
        print(f"      - {option.name : <22} {option.description} (default: {option.default})")
      else:
        print(f"      - {option.name : <22} {option.description}")

    print("")

    if adapter.EXTRA_HELP is not None:
      print(f"      {adapter.EXTRA_HELP}")
      print("")