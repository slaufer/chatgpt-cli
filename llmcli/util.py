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

def parse_api_params(params: list[str] = []) -> dict:
    return dict([
      [s.strip() for s in param.split('=', maxsplit=1)]
      for param in params
      if '=' in param
    ])

def normalize_path(path: str) -> str:
   return os.path.relpath(os.path.normpath(os.path.abspath(os.path.realpath(os.path.expanduser(path)))), os.getcwd())