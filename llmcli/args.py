import argparse
from llmcli.adapters import get_adapter_list

def get_args() -> argparse.Namespace:
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
  parser.add_argument('-p', '--api', choices=[x.NAME for x in get_adapter_list()], default='openai')
  parser.add_argument('-o', '--api-options', action='append')

  # Other arguments
  parser.add_argument('-n', '--non-interactive', action='store_true')
  parser.add_argument('-j', '--log-file-json')
  parser.add_argument('-g', '--immediate', action='store_true')
  parser.add_argument('-x', '--separator')
  parser.add_argument('-q', '--no-intro', action='store_true')
  parser.add_argument('-h', '--help', action='store_true')

  return parser.parse_args()