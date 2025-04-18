from unittest.mock import call, mock_open, patch
from llmcli.llmcli import LlmCli
from llmcli.message import Message
from random import randrange
from os import terminal_size
from base64 import b64decode

import json

TEST_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQAAAAA3bvkkAAAACklEQVR4AWNgAAAAAgABc3UBGAAAAABJRU5ErkJggg=='

def get_test_messages():
  assistant_args = {
    'adapter': 'ollama',
    'adapter_options': {
      'model': 'gemma3',
      'temperature': 0.4,
    },
    'display_name': 'ollama / gemma3',
  }

  messages = [
    Message(role='assistant', content='Hello, world!', **assistant_args),
    Message(role='user', content='How are you?'),
    Message(role='assistant', content='I am fine, thank you!', **assistant_args),
    Message(
      role='user',
      content='### File: test.txt (contents hidden)',
      file_path='test.txt',
      file_content='i\'m a file =3'
    ),
    Message(role='user', content='What is this file?'),
    Message(role='assistant', content='What a lovely file!', **assistant_args),
    Message(
      role='user',
      content='### File: test.txt (contents hidden)',
      image_path='test.png',
      image_content=TEST_IMAGE,
      image_type='image/png'
    ),
    Message(role='user', content='What is this image?'),
    Message(role='assistant', content='What a lovely image!', **assistant_args),
  ]

  return messages

def test_log_json():
  with patch('llmcli.llmcli.get_api_adapter'):
    cli = LlmCli(log_file_json='/dev/full')

  messages = get_test_messages()

  for message in messages:
    cli.add_chat_message(message=message, silent=True)

  with patch('builtins.open', mock_open()) as mock_file:
    cli.log_json()

  handle = mock_file()
  out_messages = [
    Message.from_dict(m) for m
    in json.loads(''.join([call.args[0] for call in handle.write.call_args_list]))
  ]

  assert messages == out_messages

def test_get_completion():
  with patch('llmcli.llmcli.get_api_adapter'):
    cli = LlmCli()

  messages = get_test_messages()

  for message in messages:
    cli.add_chat_message(message=message, silent=True)

  cli.get_completion()
  assert cli.api_adapter.get_completion.call_args == call(messages)

def test_get_separator():
  separator = '%030x' % randrange(16**30)

  with patch('llmcli.llmcli.get_api_adapter'):
    cli = LlmCli(separator=separator)

  assert cli.get_separator() == separator

  with patch('llmcli.llmcli.get_api_adapter'):
    cli = LlmCli()

  with patch('llmcli.llmcli.get_terminal_size', return_value=terminal_size((10, 10))):
    assert cli.get_separator() == '\n #======#\n'

def test_get_message_arg_content():
  assert LlmCli.get_message_arg_content('myargcontent') == ('myargcontent', None)
  assert LlmCli.get_message_arg_content('foo.txt') == ('foo.txt', None)

  with patch('llmcli.llmcli.sys.stdin.read', return_value='Hello World'):
    assert LlmCli.get_message_arg_content('@-') == ('Hello World', '-')

  with patch('llmcli.llmcli.os.path.exists', return_value=False):
    assert LlmCli.get_message_arg_content('@bar.txt') == (None, 'bar.txt')

  with \
    patch('llmcli.llmcli.os.path.exists', return_value=True), \
    patch('builtins.open', mock_open(read_data='beep boop')):

    assert LlmCli.get_message_arg_content('@baz.txt') == ('beep boop', 'baz.txt')

actual_open = open

def mock_open_side_effect(file, *args, **kwargs):
  if file == 'file.txt':
    return mock_open(read_data='beep boop').return_value
  elif file == 'image.png':
    m = mock_open()
    m.return_value.read.return_value = b64decode(TEST_IMAGE)
    return m.return_value
  else:
    return actual_open(file, *args, **kwargs)

def test_add_messages_from_args():
  with patch('llmcli.llmcli.get_api_adapter'):
    cli = LlmCli(interactive=False)


  with \
    patch('llmcli.llmcli.os.path.exists', return_value=True), \
    patch('builtins.open') as mock_open:

    mock_open.side_effect = mock_open_side_effect
    
    cli.add_messages_from_args(args=[
      '-s', 'you are a jelly donut',
      '-n', '-q',
      '-u', 'what are you?',
      '-p', 'ollama',
      '-a', 'i am a jelly donut',
      '-u', '@file.txt',
      '-x', ' =3 =3 =3 ',
      '-a', '@file.txt',
      '-f', 'file.txt',
      '-i', 'image.png',
    ])

  assert cli.messages == [
    Message(role='system', content='you are a jelly donut'),
    Message(role='user', content='what are you?'),
    Message(role='assistant', content='i am a jelly donut'),
    Message(role='user', content='beep boop'),
    Message(role='assistant', content='beep boop'),
    Message(role='user', file_path='file.txt', file_content='beep boop'),
    Message(role='user', image_path='image.png', image_content=TEST_IMAGE, image_type='image/png'),
  ]