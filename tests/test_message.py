from llmcli.message import Message
from unittest.mock import patch, mock_open
from base64 import b64encode
import json

def test_load_files():
    with \
      patch('builtins.open', mock_open(read_data='file content')), \
      patch('llmcli.util.os.getcwd', return_value='/home/user'):

      file_message = Message(file_path='test.txt')
      assert file_message.file_content == 'file content'
      assert file_message.file_path == 'test.txt'
      assert file_message.content == f'### File: test.txt (contents hidden)'

    with \
      patch('builtins.open', mock_open(read_data=b'image content')), \
      patch('llmcli.util.os.getcwd', return_value='/home/user'), \
      patch('llmcli.message.get_mime_type', return_value='image/png'):

      image_message = Message(image_path='/path/to/image.png')
      assert image_message.image_type == 'image/png'
      assert image_message.image_path == '../../path/to/image.png'
      assert image_message.image_content == b64encode(b'image content').decode('utf-8')
      assert image_message.content == f'### Image: ../../path/to/image.png (image/png) (contents hidden)'

def test_from_to_dict():
  message_dict = {
    'role': 'assistant',
    'content': 'Hello, world!',
    'adapter': 'openai',
    'adapter_options': {
      'api_key': 'your_api_key',
      'model': 'gpt-3.5-turbo',
      'temperature': 0.7,
    },
    'display_name': 'Assistant',
  }

  assert Message.from_dict(message_dict).to_dict() == message_dict

def test_from_to_json():
  message_json = json.dumps({
    'role': 'assistant',
    'content': 'Hello, world!',
    'adapter': 'openai',
    'adapter_options': {
      'api_key': 'your_api_key',
      'model': 'gpt-3.5-turbo',
      'temperature': 0.7,
    },
    'display_name': 'Assistant',
  })

  assert Message.from_json(message_json).to_json() == message_json