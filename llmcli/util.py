import argparse
import mimetypes
import os

def get_mime_type(image_path: str) -> str:
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
  parser.add_argument('-p', '--api', choices=['openai', 'anthropic', 'ollama'], default='openai')
  parser.add_argument('-o', '--api-options', action='append')

  # Other arguments
  parser.add_argument('-n', '--non-interactive', action='store_true')
  parser.add_argument('-j', '--log-file-json')
  parser.add_argument('-g', '--immediate', action='store_true')
  parser.add_argument('-x', '--separator')
  parser.add_argument('-q', '--no-intro', action='store_true')
  parser.add_argument('-h', '--help', action='store_true')

  return parser.parse_args()

def parse_api_params(params: list[str] = []) -> dict:
    return dict([
      [s.strip() for s in param.split('=')]
      for param in params
      if '=' in param
    ])

def normalize_path(path: str) -> str:
   return os.path.relpath(os.path.abspath(os.path.expanduser(path)), os.getcwd())