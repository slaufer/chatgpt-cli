"""
This module provides the AnthropicApiAdapter class, which integrates with the Anthropic API
to generate completions and handle streaming responses.

The adapter supports configuration options such as model selection, API key, and generation
parameters like max tokens, temperature, and top-p sampling.
"""

import os

from typing import Iterable, Tuple
import anthropic
from anthropic import NOT_GIVEN

from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption
from llmcli.messages.message import Message
from llmcli.messages.file_message import FileMessage
from llmcli.messages.image_message import ImageMessage


class AnthropicApiAdapter(BaseApiAdapter):
    """
    Adapter for interacting with the Anthropic API.

    Attributes
    ----------
    NAME : str
        The identifier for the adapter.
    HR_NAME : str
        The human-readable name for the adapter.
    EXTRA_HELP : str
        Additional help text for the adapter.
    MASKED_OPTIONS : set
        Configuration options that should be masked in logs or outputs.
    OPTIONS : list[ApiAdapterOption]
        List of configuration options supported by the adapter.

    Parameters
    ----------
    params : dict
        A dictionary of configuration parameters for the adapter.
    """
    NAME = "anthropic"
    HR_NAME = "Anthropic"
    EXTRA_HELP = (
        "By default, uses the Anthropic API key from the environment variable ANTHROPIC_API_KEY."
    )
    MASKED_OPTIONS = set("api_key")
    OPTIONS = [
        ApiAdapterOption(
            name="model",
            hr_name="Model",
            description="Model ID used to generate the response.",
            default="claude-3-7-sonnet-latest",
        ),
        ApiAdapterOption(
            name="api_key",
            hr_name="API Key",
            description="Your Anthropic API key",
            default=os.environ.get("ANTHROPIC_API_KEY"),
            default_help_override="ANTHROPIC_API_KEY",
        ),
        ApiAdapterOption(
            name="max_tokens",
            hr_name="Max Tokens",
            description="The maximum number of tokens that can be generated in the chat completion",
            default=1000,
        ),
        ApiAdapterOption(
            name="temperature",
            hr_name="Temperature",
            description="What sampling temperature to use, between 0 and 2.",
        ),
        ApiAdapterOption(
            name="top_p",
            hr_name="Top P",
            description="An alternative to sampling with temperature, called nucleus sampling.",
        ),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.client = anthropic.Anthropic(api_key=self.get_config('api_key'))
        self.system = None

    @staticmethod
    def output_stream(
        response_stream: anthropic.Stream,
        response_message: Message,
    ) -> Iterable[str]:
        """
        Process the streaming response from the Anthropic API.

        Parameters
        ----------
        response_stream : anthropic.Stream
            The streaming response object from the API.
        response_message : Message
            The message object to update with the response content.

        Yields
        ------
        str
            Fragments of the response content as they are received.
        """
        for chunk in response_stream:
            if chunk.type != "content_block_delta" or chunk.delta.type != "text_delta":
                continue

            fragment = chunk.delta.text
            response_message.content += fragment
            yield fragment

    def get_completion(
        self,
        input_messages: list[Message],
    ) -> Tuple[Iterable[str] | None, Message]:
        """
        Generate a completion using the Anthropic API.

        Parameters
        ----------
        input_messages : list[Message]
            A list of input messages to send to the API.

        Returns
        -------
        stream : Iterable[str] | None
            Text output stream.
        message : Message
            The Message object with metadata. (See Notes for important information.)

        Notes
        -----
        The `content` field of the returned Message object should not be to be considered fully
        populated until the Iterable is fully consumed.
        The Anthropic API requires consecutive messages of the same role to be merged.
        """
        messages = []

        for message in input_messages:
            if message.role == "system":
                self.system = message.content
                continue

            if isinstance(message, FileMessage):
                out_message = {
                    "role": message.role,
                    "content": [
                        {
                            "type": "text",
                            "text": f"### FILE: {message.file_path}\n\n" + \
                                f"```\n{message.file_content}\n```",
                        }
                    ],
                }
            elif isinstance(message, ImageMessage):
                out_message = {
                    "role": message.role,
                    "content": [
                        {
                            "type": "text",
                            "text": f"### IMAGE: {message.image_path}",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": message.image_type,
                                "data": message.image_content,
                            },
                        },
                    ],
                }
            else:
                out_message = {
                    "role": message.role,
                    "content": [{"type": "text", "text": message.content}],
                }

            # Merge consecutive messages of the same role (required by Anthropic API)
            if len(messages) > 0 and messages[-1].get("role") == out_message.get("role"):
                messages[-1]["content"] += out_message.get("content")
            else:
                messages.append(out_message)

        response_stream = self.client.messages.create(
            max_tokens=self.get_config('max_tokens', cast=int),
            model=self.get_config('model'),
            messages=messages,
            stream=True,
            temperature=self.get_config('temperature', cast=float, default=NOT_GIVEN),
            top_p=self.get_config('top_p', cast=float, default=NOT_GIVEN),
            system=self.system or NOT_GIVEN,
        )

        response_message = Message(
            role="assistant",
            content="",
            adapter=self.NAME,
            adapter_options=self.get_masked_config(),
            display_name=self.get_display_name(),
        )

        return self.output_stream(response_stream, response_message), response_message
