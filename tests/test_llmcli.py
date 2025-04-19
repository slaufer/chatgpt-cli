import json

from unittest.mock import call, mock_open, patch
from random import randrange
from os import terminal_size
from base64 import b64decode

from llmcli.llmcli import LlmCli
from llmcli.messages.message import Message
from llmcli.messages.file_message import FileMessage
from llmcli.messages.image_message import ImageMessage
from llmcli.messages import message_from_dict

from tests.fixtures.messages import get_test_messages, TEST_IMAGE


def test_log_json():
    with patch("llmcli.llmcli.get_api_adapter"):
        cli = LlmCli(log_file_json="/dev/full")

    messages = get_test_messages(image=True, file=True)

    for message in messages:
        cli.add_chat_message(message=message, silent=True)

    with patch("builtins.open", mock_open()) as mock_file:
        cli.log_json()

    handle = mock_file()
    out_messages = [
        message_from_dict(m)
        for m in json.loads("".join([call.args[0] for call in handle.write.call_args_list]))
    ]

    assert messages == out_messages


def test_get_completion():
    with patch("llmcli.llmcli.get_api_adapter"):
        cli = LlmCli()

    messages = get_test_messages(image=True, file=True)

    for message in messages:
        cli.add_chat_message(message=message, silent=True)

    cli.get_completion()
    assert cli.api_adapter.get_completion.call_args == call(messages)


def test_get_separator():
    separator = "%030x" % randrange(16**30)

    with patch("llmcli.llmcli.get_api_adapter"):
        cli = LlmCli(separator=separator)

    assert cli.get_separator() == separator

    with patch("llmcli.llmcli.get_api_adapter"):
        cli = LlmCli()

    with patch("llmcli.llmcli.get_terminal_size", return_value=terminal_size((10, 10))):
        assert cli.get_separator() == "\n #======#\n"


def test_get_message_arg_content():
    assert LlmCli.get_message_arg_content("myargcontent") == ("myargcontent", None)
    assert LlmCli.get_message_arg_content("foo.txt") == ("foo.txt", None)

    with patch("llmcli.llmcli.sys.stdin.read", return_value="Hello World"):
        assert LlmCli.get_message_arg_content("@-") == ("Hello World", "-")

    with patch("llmcli.llmcli.os.path.exists", return_value=False):
        assert LlmCli.get_message_arg_content("@bar.txt") == (None, "bar.txt")

    with patch("llmcli.llmcli.os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data="beep boop")
    ):
        assert LlmCli.get_message_arg_content("@baz.txt") == ("beep boop", "baz.txt")


actual_open = open


def mock_open_side_effect(file, *args, **kwargs):
    if file == "file.txt":
        return mock_open(read_data="beep boop").return_value
    
    if file == "image.png":
        m = mock_open()
        m.return_value.read.return_value = b64decode(TEST_IMAGE)
        return m.return_value
    
    if file == "log.json":
        m = mock_open()
        m.return_value.read.return_value = "[{\"message_type\":\"Message\",\"role\":\"assista" + \
            "nt\",\"content\":\"this is a text message\"},{\"message_type\":\"FileMessage\"," + \
            "\"role\":\"user\",\"content\":\"### File: file.txt\",\"file_path\":\"file.txt\"," +\
            "\"file_content\":\"beep boop\"}]"

        return m.return_value
    
    return actual_open(file, *args, **kwargs)


def test_add_messages_from_args():
    # TODO: test -c
    # TODO: break this test up
    with patch("llmcli.llmcli.get_api_adapter"):
        cli = LlmCli(interactive=False)

    with patch("llmcli.llmcli.os.path.exists", return_value=True), patch(
        "builtins.open"
    ) as mocked_open:
        mocked_open.side_effect = mock_open_side_effect

        cli.add_messages_from_args(
            args=[
                "-s", "you are a jelly donut",
                "-u", "what are you?",
                "-a", "i am a jelly donut",
                "-u", "@file.txt",
                "-a", "@file.txt",
                "-f", "file.txt",
                "-i", "image.png",
                "-c", "@log.json",
            ]
        )

    assert cli.messages == [
        Message(role="system", content="you are a jelly donut"),
        Message(role="user", content="what are you?"),
        Message(role="assistant", content="i am a jelly donut"),
        Message(role="user", content="beep boop"),
        Message(role="assistant", content="beep boop"),
        FileMessage(role="user", file_path="file.txt", file_content="beep boop"),
        ImageMessage(
            role="user",
            image_path="image.png",
            image_content=TEST_IMAGE,
            image_type="image/png",
        ),
        Message(role="assistant", content="this is a text message"),
        FileMessage(
            role="user",
            file_content="beep boop",
            file_path="file.txt",
            content="### File: file.txt"
        ),
    ]
