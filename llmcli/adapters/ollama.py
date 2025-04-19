from typing import Iterable, Tuple
import ollama

from llmcli.adapters.base import BaseApiAdapter, ApiAdapterOption
from llmcli.messages.message import Message
from llmcli.messages.file_message import FileMessage
from llmcli.messages.image_message import ImageMessage


class OllamaApiAdapter(BaseApiAdapter):
    NAME = "ollama"
    HR_NAME = "Ollama"
    EXTRA_HELP = "By default, uses an Ollama instance running on localhost. For remote " + \
        "instances, set the OLLAMA_HOST environment variable."
    MASKED_OPTIONS = set()
    OPTIONS = [
        ApiAdapterOption(
            name="model",
            hr_name="Model",
            description="Model ID used to generate the response.",
            default="llama3.1:8b",
        ),
        ApiAdapterOption(
            name="mirostat",
            hr_name="Mirostat",
            description="Enable Mirostat sampling for controlling perplexity.",
        ),
        ApiAdapterOption(
            name="mirostat_eta",
            hr_name="Mirostat Eta",
            description=
              "Influences how quickly the algorithm responds to feedback from the generated text.",
        ),
        ApiAdapterOption(
            name="mirostat_tau",
            hr_name="Mirostat Tau",
            description="Controls the balance between coherence and diversity of the output.",
        ),
        ApiAdapterOption(
            name="num_ctx",
            hr_name="Context Size",
            description="Sets the size of the context window used to generate the next token.",
        ),
        ApiAdapterOption(
            name="repeat_last_n",
            hr_name="Repeat Last N",
            description="Sets how far back for the model to look back to prevent repetition.",
        ),
        ApiAdapterOption(
            name="repeat_penalty",
            hr_name="Repeat Penalty",
            description="Sets how strongly to penalize repetitions.",
        ),
        ApiAdapterOption(
            name="temperature",
            hr_name="Temperature",
            description="The temperature of the model; higher values increase creativity.",
        ),
        ApiAdapterOption(
            name="seed",
            hr_name="Seed",
            description="Sets the random number seed to use for generation.",
        ),
        ApiAdapterOption(
            name="num_predict",
            hr_name="Max Tokens",
            description="Maximum number of tokens to predict when generating text.",
        ),
        ApiAdapterOption(
            name="top_k",
            hr_name="Top-K",
            description=
              "Reduces the probability of generating nonsense by limiting token selection.",
        ),
        ApiAdapterOption(
            name="top_p",
            hr_name="Top-P",
            description=
              "Controls diversity via nucleus sampling; higher values yield more diverse text.",
        ),
    ]

    @staticmethod
    def output_stream(response_stream: Iterable[dict], response_message: Message) -> Iterable[str]:
        for chunk in response_stream:
            fragment = chunk["message"]["content"]
            response_message.content += fragment
            yield fragment

    def get_completion(
        self, input_messages: list[Message]
    ) -> Tuple[Iterable[str] | None, Message]:
        messages = []

        for message in input_messages:
            if isinstance(message, FileMessage):
                messages.append(
                    {
                        "role": message.role,
                        "content": f"### FILE: {message.file_path}\n\n" + \
                            f"```\n{message.file_content}\n```",
                    }
                )
            elif isinstance(message, ImageMessage):
                messages.append(
                    {
                        "role": message.role,
                        "content": f"### IMAGE: {message.image_path}",
                        "images": [message.image_content],
                    }
                )
            else:
                messages.append({"role": message.role, "content": message.content})

        options = ollama.Options(
            mirostat=self.get_config('mirostat', cast=int),
            mirostat_eta=self.get_config('mirostat_eta', cast=float),
            mirostat_tau=self.get_config('mirostat_tau', cast=float),
            num_ctx=self.get_config('num_ctx', cast=int),
            repeat_last_n=self.get_config('repeat_last_n', cast=int),
            repeat_penalty=self.get_config('repeat_penalty', cast=float),
            temperature=self.get_config('temperature', cast=float),
            seed=self.get_config('seed', cast=int),
            num_predict=self.get_config('num_predict', cast=int),
            top_k=self.get_config('top_k', cast=int),
            top_p=self.get_config('top_p', cast=float),
        )

        response_stream = ollama.chat(
            model=self.get_config('model'),
            messages=messages,
            options=options,
            stream=True,
        )

        response_message = Message(
            role="assistant",
            content="",
            adapter=self.NAME,
            adapter_options=self.get_masked_config(),
            display_name=self.get_display_name(),
        )

        return self.output_stream(response_stream, response_message), response_message
