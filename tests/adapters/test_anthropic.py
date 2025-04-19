from unittest.mock import MagicMock, patch

import re

from llmcli.adapters.anthropic import AnthropicApiAdapter
from tests.fixtures.messages import get_test_messages


def mock_response_stream(response_str):
    for token in re.split(r"(\s+)", response_str):
        yield MagicMock(type="content_block_delta", delta=MagicMock(type="text_delta", text=token))


def get_adapter_with_mock_client(params, response_str):
    with patch("llmcli.adapters.anthropic.anthropic.Anthropic") as mock_Anthropic:
        adapter = AnthropicApiAdapter(params)
        adapter.client.messages.create.side_effect = lambda *args, **kwargs: mock_response_stream(
            response_str
        )
        return adapter, mock_Anthropic


def get_sanity_checked_adapter(messages):
    test_params = {
        "api_key": "sk-ant-1234567890abcdef1234567890abcdef1234567890abcdef",
        "model": "claude-3-7-sonnet-latest",
        "temperature": "1.7",
        "top_p": "0.9",
    }
    test_message = "this is a test"
    adapter, mock_Anthropic = get_adapter_with_mock_client(test_params, test_message)

    stream, message = adapter.get_completion(messages)

    # these need to be in order, because the message content isn't fully populated until the stream is consumed
    assert message.content != test_message
    assert "".join(stream) == test_message
    assert message.content == test_message

    mock_Anthropic.assert_called_with(api_key=test_params["api_key"])

    return adapter


def test_anthropic_api_adapter_text_only():
    messages = get_test_messages()
    adapter = get_sanity_checked_adapter(messages)

    adapter.client.messages.create.assert_called_with(
        max_tokens=1000,
        model="claude-3-7-sonnet-latest",
        temperature=1.7,
        top_p=0.9,
        system="You are an assistant.",
        messages=[
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello, world!"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "How are you?"},
                    {"type": "text", "text": "You are how?"},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "I am fine, thank you!"}],
            },
        ],
        stream=True,
    )


def test_anthropic_api_adapter_image():
    messages = get_test_messages(text=False, image=True)
    adapter = get_sanity_checked_adapter(messages)

    adapter.client.messages.create.assert_called_with(
        max_tokens=1000,
        model="claude-3-7-sonnet-latest",
        temperature=1.7,
        top_p=0.9,
        system="You are an assistant.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "### IMAGE: test.png"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQAAAAA3bvkkAAAACklEQVR4AWNgAAAAAgABc3UBGAAAAABJRU5ErkJggg==",
                        },
                    },
                    {"type": "text", "text": "What is this image?"},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "What a lovely image!"}],
            },
        ],
        stream=True,
    )


def test_anthropic_api_adapter_file():
    messages = get_test_messages(text=False, file=True)
    adapter = get_sanity_checked_adapter(messages)

    adapter.client.messages.create.assert_called_with(
        max_tokens=1000,
        model="claude-3-7-sonnet-latest",
        temperature=1.7,
        top_p=0.9,
        system="You are an assistant.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "### FILE: test.txt\n\n```\ni'm a file =3\n```",
                    },
                    {"type": "text", "text": "What is this file?"},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "What a lovely file!"}],
            },
        ],
        stream=True,
    )
