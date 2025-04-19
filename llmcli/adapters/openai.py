import os
from typing import Iterable, Tuple, Union

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption
from llmcli.message import Message


class OpenAiApiAdapter(BaseApiAdapter):
    NAME = "openai"
    HR_NAME = "OpenAI"
    OPTIONS = [
        ApiAdapterOption(
            name="model",
            hr_name="Model",
            description="Model ID used to generate the response.",
            default="gpt-4o",
        ),
        ApiAdapterOption(
            name="api_key",
            hr_name="API Key",
            description="Your OpenAI API key",
            default=os.environ.get("OPENAI_API_KEY"),
            default_help_override="OPENAI_API_KEY",
        ),
        ApiAdapterOption(
            name="max_tokens",
            hr_name="Max Tokens",
            description="The maximum number of tokens that can be generated in the chat completion.",
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
        ApiAdapterOption(
            name="frequency_penalty",
            hr_name="Frequency Penalty",
            description="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far.",
        ),
        ApiAdapterOption(
            name="presence_penalty",
            hr_name="Presence Penalty",
            description="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far.",
        ),
    ]
    EXTRA_HELP = "By default, uses the OpenAI API key from the environment variable OPENAI_API_KEY."

    # used when an image message is submitted without a MAX_TOKENS setting
    SAFE_MAX_TOKENS = 1000

    def __init__(self, params):
        super().__init__(params)
        self.client = OpenAI(api_key=self.config.get("api_key"))

    @staticmethod
    def output_stream(
        response_stream: Stream[ChatCompletionChunk], response_message: Message
    ) -> Iterable[str]:
        for chunk in response_stream:
            fragment = chunk.choices[0].delta.content

            if fragment is None:
                continue

            response_message.content += fragment
            yield fragment

    def get_completion(
        self, input_messages: list[Message]
    ) -> Tuple[Union[Iterable[str], None], Message]:
        messages = []
        max_tokens = self.config.get("max_tokens")

        for message in input_messages:
            if message.file_content is not None:
                messages.append(
                    {
                        "role": message.role,
                        "content": f"### FILE: {message.file_path}\n\n```\n{message.file_content}\n```",
                    }
                )
            elif message.image_content is not None:
                if max_tokens is None:
                    max_tokens = self.SAFE_MAX_TOKENS

                messages.append(
                    {
                        "role": message.role,
                        "content": [
                            {
                                "type": "text",
                                "text": f"### IMAGE: {message.image_path}",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:"
                                    + message.image_type
                                    + ";base64,"
                                    + message.image_content
                                },
                            },
                        ],
                    }
                )
            else:
                messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        req = {
            "messages": messages,
            "model": self.config.get("model"),
            "stream": True,
        }

        if max_tokens is not None:
            req["max_tokens"] = int(max_tokens)

        if self.config.get("temperature") is not None:
            req["temperature"] = float(self.config.get("temperature"))

        if self.config.get("top_p") is not None:
            req["top_p"] = float(self.config.get("top_p"))

        if self.config.get("frequency_penalty") is not None:
            req["frequency_penalty"] = float(self.config.get("frequency_penalty"))

        if self.config.get("presence_penalty") is not None:
            req["presence_penalty"] = float(self.config.get("presence_penalty"))

        response_stream = self.client.chat.completions.create(**req)

        response_message = Message(
            role="assistant",
            content="",
            adapter=self.NAME,
            adapter_options={
                k: v for k, v in self.config.items() if k != "api_key" and v is not None
            },
            display_name=self.get_display_name(),
        )

        return self.output_stream(response_stream, response_message), response_message
