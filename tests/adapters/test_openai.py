from unittest.mock import MagicMock, patch

import re
from random import random, choice

from llmcli.adapters.openai import OpenAiApiAdapter
from tests.fixtures.messages import get_test_messages

def mock_response_stream(str):
  for token in re.split(r'(\s+)', str):
    chunk = MagicMock()
    chunk.choices = [MagicMock(delta=MagicMock(content=token))]
    yield chunk

def get_adapter_with_mock_client(params, response_str):
  with patch('llmcli.adapters.openai.OpenAI') as mock_OpenAI:
    adapter = OpenAiApiAdapter(params)
    adapter.client.chat.completions.create.side_effect = lambda *args, **kwargs: mock_response_stream(response_str)
    return adapter, mock_OpenAI

def get_sanity_checked_adapter(messages):
  test_params = {
    'api_key': 'test-key',
    'model': choice(['gpt-4o', 'chatgpt-4o-latest', 'o3', 'gpt-4.1-mini']),
    'temperature': str(random() * 2),
    'top_p': str(random()),
    'frequency_penalty': str(random() * 4 - 2),
    'presence_penalty': str(random() * 4 - 2),
  }
  test_message = "this is a test"
  adapter, mock_OpenAI = get_adapter_with_mock_client(test_params, test_message)

  stream, message = adapter.get_completion(messages)

  # these need to be in order, because the message content isn't fully populated until the stream is consumed
  assert message.content != test_message
  assert ''.join(stream) == test_message
  assert message.content == test_message

  mock_OpenAI.call_args.assert_called_with(api_key=test_params['api_key'])

  return adapter, {
    'model': test_params['model'],
    'temperature': float(test_params['temperature']),
    'top_p': float(test_params['top_p']),
    'frequency_penalty': float(test_params['frequency_penalty']),
    'presence_penalty': float(test_params['presence_penalty']),
  }

def test_openai_api_adapter_text_only():
  messages = get_test_messages()
  adapter, call_params = get_sanity_checked_adapter(messages)

  adapter.client.chat.completions.create.assert_called_with(
    messages=[{'role': m.role, 'content': m.content} for m in messages],
    stream=True,
    **call_params,
  )

def test_openai_api_adapter_image():
  messages = get_test_messages(text=False, image=True)
  adapter, call_params = get_sanity_checked_adapter(messages)

  adapter.client.chat.completions.create.assert_called_with(
    messages=[
      {
        'role': m.role,
        'content': [
          { 'type': 'text', 'text': f'### IMAGE: {m.image_path}' },
          {
            'type': 'image_url',
            'image_url': {
              'url': f'data:{m.image_type};base64,{m.image_content}',
            }
          }
        ]
      } if m.image_content is not None else {
        'role': m.role,
        'content': m.content,
      }
      for m in messages
    ],
    max_tokens=OpenAiApiAdapter.SAFE_MAX_TOKENS,
    stream=True,
    **call_params,
  )

def test_openai_api_adapter_file():
  messages = get_test_messages(text=False, file=True)
  adapter, call_params  = get_sanity_checked_adapter(messages)

  adapter.client.chat.completions.create.assert_called_with(
    messages=[
      {
        'role': m.role,
        'content': f'### FILE: {m.file_path}\n\n```\n{m.file_content}\n```' if m.file_content is not None else m.content,
      }
      for m in messages
    ],
    stream=True,
    **call_params,
  )