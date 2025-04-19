from unittest.mock import MagicMock, patch

import re

from llmcli.adapters.openai import OpenAiApiAdapter
from tests.fixtures.messages import get_test_messages

def mock_response_stream(response_str):
  for token in re.split(r'(\s+)', response_str):
    yield MagicMock(choices=[MagicMock(delta=MagicMock(content=token))])

def get_adapter_with_mock_client(params, response_str):
  with patch('llmcli.adapters.openai.OpenAI') as mock_OpenAI:
    adapter = OpenAiApiAdapter(params)
    adapter.client.chat.completions.create.side_effect = lambda *args, **kwargs: mock_response_stream(response_str)
    return adapter, mock_OpenAI

def get_sanity_checked_adapter(messages):
  test_params = {
    'api_key': 'sk-abcdefghijklmnopqrstuvwxyz1234567890abcdef',
    'model': 'chatgpt-4o-latest',
    'temperature': '1.313',
    'top_p': '0.49',
    'frequency_penalty': '-1.1',
    'presence_penalty': '-0.998',
  }
  test_message = "this is a test"
  adapter, mock_OpenAI = get_adapter_with_mock_client(test_params, test_message)

  stream, message = adapter.get_completion(messages)

  # these need to be in order, because the message content isn't fully populated until the stream is consumed
  assert message.content != test_message
  assert ''.join(stream) == test_message
  assert message.content == test_message

  mock_OpenAI.call_args.assert_called_with(api_key=test_params['api_key'])

  return adapter

def test_openai_api_adapter_text_only():
  messages = get_test_messages()
  adapter = get_sanity_checked_adapter(messages)

  adapter.client.chat.completions.create.assert_called_with(
    messages=[
      {'role': 'system', 'content': 'You are an assistant.'},
      {'role': 'assistant', 'content': 'Hello, world!'},
      {'role': 'user', 'content': 'How are you?'},
      {'role': 'user', 'content': 'You are how?'},
      {'role': 'assistant', 'content': 'I am fine, thank you!'}
    ],
    model='chatgpt-4o-latest',
    stream=True,
    temperature=1.313,
    top_p=0.49,
    frequency_penalty=-1.1,
    presence_penalty=-0.998,
  )

def test_openai_api_adapter_image():
  messages = get_test_messages(text=False, image=True)
  adapter = get_sanity_checked_adapter(messages)

  adapter.client.chat.completions.create.assert_called_with(
    messages=[
      {'role': 'system', 'content': 'You are an assistant.'},
      {
        'role': 'user',
        'content': [
          {'type': 'text', 'text': '### IMAGE: test.png'},
          {
            'type': 'image_url',
            'image_url': {
              'url': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQAAAAA3bvkkAAAACklEQVR4AWNgAAAAAgABc3UBGAAAAABJRU5ErkJggg=='
            }
          }
        ]
      },
      {'role': 'user', 'content': 'What is this image?'},
      {'role': 'assistant', 'content': 'What a lovely image!'}
    ],
    model='chatgpt-4o-latest',
    stream=True,
    max_tokens=1000,
    temperature=1.313,
    top_p=0.49,
    frequency_penalty=-1.1,
    presence_penalty=-0.998,
  )

def test_openai_api_adapter_file():
  messages = get_test_messages(text=False, file=True)
  adapter = get_sanity_checked_adapter(messages)

  adapter.client.chat.completions.create.assert_called_with(
    messages=[
      {'role': 'system', 'content': 'You are an assistant.'},
      {'role': 'user', 'content': "### FILE: test.txt\n\n```\ni'm a file =3\n```"},
      {'role': 'user', 'content': 'What is this file?'},
      {'role': 'assistant', 'content': 'What a lovely file!'}
    ],
    model='chatgpt-4o-latest',
    stream=True,
    temperature=1.313,
    top_p=0.49,
    frequency_penalty=-1.1,
    presence_penalty=-0.998
  )