import os
import json
import base64

from llmcli.util import get_mime_type

class Message:
  def __init__(
      self,
      role='user',
      content='',
      image_content=None,
      image_path=None,
      image_type=None,
      file_content=None,
      file_path=None,
      adapter='none',
      adapter_options=None,
      display_name=None,
      extra=None
  ) -> None:
    self.role = role
    self.content = content
    self.file_content = file_content
    self.file_path = file_path
    self.image_content = image_content
    self.image_path = image_path
    self.image_type = image_type
    self.adapter = adapter
    self.adapter_options = adapter_options or {}
    self.display_name = display_name or role.capitalize()
    self.extra = extra

    self.load_files()

  def load_files(self) -> None:
    if self.file_path is not None:
      self.file_path = os.path.relpath(os.path.abspath(self.file_path), os.getcwd())

      if self.file_content is None:
        with open(self.file_path, 'r') as file:
          self.file_content = file.read()

      self.content = f'### File: {self.file_path} (contents hidden)'


    elif self.image_path is not None:
      self.image_path = os.path.relpath(os.path.abspath(self.image_path), os.getcwd())

      if self.image_content is None:
        with open(self.image_path, 'rb') as file:
          self.image_content = base64.b64encode(file.read()).decode('utf-8')

      if self.image_type is None:
        self.image_type = get_mime_type(self.image_path)

      self.content = f'### Image: {self.image_path} ({self.image_type}) (contents hidden)'

  def to_dict(self) -> dict:
    return {k: v for k, v in self.__dict__.items() if v is not None}
  
  def to_json(self) -> str:
    return json.dumps(self.to_dict())
  
  @staticmethod
  def from_dict(data: dict) -> "Message":
    return Message(**data)
  
  @classmethod
  def from_json(cls, json_str: str) -> "Message":
    data = json.loads(json_str)
    return cls.from_dict(data)