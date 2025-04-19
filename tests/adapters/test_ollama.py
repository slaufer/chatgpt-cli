from unittest.mock import MagicMock, patch

import re

from llmcli.adapters.ollama import OllamaApiAdapter
from tests.fixtures.messages import get_test_messages
from ollama import Options


def mock_response_stream(response_str):
    for token in re.split(r"(\s+)", response_str):
        yield {"message": {"content": token}}


def sanity_check_adapter(messages, test_message):
    test_params = {
        "model": "gemma3",
        "mirostat": "1",
        "mirostat_tau": "0.8",
        "mirostat_eta": "0.6",
        "num_ctx": "1024",
        "repeat_last_n": "33",
        "repeat_penalty": "1.2",
        "temperature": "0.8",
        "seed": "42",
        "num_predict": "100",
        "top_k": "20",
        "top_p": "0.9",
    }

    adapter = OllamaApiAdapter(test_params)

    stream, message = adapter.get_completion(messages)

    # these need to be in order, because the message content isn't fully populated until the stream is consumed
    assert message.content != test_message
    assert "".join(stream) == test_message
    assert message.content == test_message

    return adapter


@patch("llmcli.adapters.ollama.ollama.chat")
def test_ollama_api_adapter_text_only(mock_chat):
    test_message = "this is a test"
    mock_chat.side_effect = lambda *args, **kwargs: mock_response_stream(test_message)
    messages = get_test_messages()
    sanity_check_adapter(messages, test_message)

    mock_chat.assert_called_with(
        model="gemma3",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "assistant", "content": "Hello, world!"},
            {"role": "user", "content": "How are you?"},
            {"role": "user", "content": "You are how?"},
            {"role": "assistant", "content": "I am fine, thank you!"},
        ],
        options=Options(
            num_ctx=1024,
            seed=42,
            num_predict=100,
            top_k=20,
            top_p=0.9,
            repeat_last_n=33,
            temperature=0.8,
            repeat_penalty=1.2,
            mirostat=1,
            mirostat_tau=0.8,
            mirostat_eta=0.6,
        ),
        stream=True,
    )


@patch("llmcli.adapters.ollama.ollama.chat")
def test_ollama_api_adapter_image(mock_chat):
    test_message = "this is a test"
    mock_chat.side_effect = lambda *args, **kwargs: mock_response_stream(test_message)
    messages = get_test_messages(text=False, image=True)
    sanity_check_adapter(messages, test_message)

    mock_chat.assert_called_with(
        model="gemma3",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {
                "role": "user",
                "content": "### IMAGE: test.png",
                "images": [
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQAAAAA3bvkkAAAACklEQVR4AWNgAAAAAgABc3UBGAAAAABJRU5ErkJggg=="
                ],
            },
            {"role": "user", "content": "What is this image?"},
            {"role": "assistant", "content": "What a lovely image!"},
        ],
        options=Options(
            num_ctx=1024,
            seed=42,
            num_predict=100,
            top_k=20,
            top_p=0.9,
            repeat_last_n=33,
            temperature=0.8,
            repeat_penalty=1.2,
            mirostat=1,
            mirostat_tau=0.8,
            mirostat_eta=0.6,
        ),
        stream=True,
    )


@patch("llmcli.adapters.ollama.ollama.chat")
def test_ollama_api_adapter_file(mock_chat):
    test_message = "this is a test"
    mock_chat.side_effect = lambda *args, **kwargs: mock_response_stream(test_message)
    messages = get_test_messages(text=False, file=True)
    sanity_check_adapter(messages, test_message)

    mock_chat.assert_called_with(
        model="gemma3",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {
                "role": "user",
                "content": "### FILE: test.txt\n\n```\ni'm a file =3\n```",
            },
            {"role": "user", "content": "What is this file?"},
            {"role": "assistant", "content": "What a lovely file!"},
        ],
        options=Options(
            num_ctx=1024,
            seed=42,
            num_predict=100,
            top_k=20,
            top_p=0.9,
            repeat_last_n=33,
            temperature=0.8,
            repeat_penalty=1.2,
            mirostat=1,
            mirostat_tau=0.8,
            mirostat_eta=0.6,
        ),
        stream=True,
    )
