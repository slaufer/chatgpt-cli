import os
import sys
import json

from shutil import get_terminal_size
from typing import Any, Iterable, Tuple, Union

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from llmcli.args import get_args
from llmcli.util import parse_api_params, normalize_path
from llmcli.help import print_help, INTERACTIVE_KEYS
from llmcli.adapters import get_api_adapter, get_adapter_list
from llmcli.messages.message import Message
from llmcli.messages.file_message import FileMessage
from llmcli.messages.image_message import ImageMessage
from llmcli.messages import message_from_dict

DEFAULT_SYSTEM_PROMPT = """
Carefully heed the user's instructions.
Respond using Markdown.
Respond briefly and concisely unless you are instructed to do otherwise.
Do not include any extraneous or tangential details unless you are instructed to do otherwise.
""".strip()


class LlmCli:
    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(
        self,
        log_file_json: str | None = None,
        interactive=True,
        immediate=False,
        separator=None,
        intro=True,
        no_system_prompt=False,
        api_adapter_name=None,
        api_adapter_options=None,
    ):
        self.json_log_file = normalize_path(log_file_json) if log_file_json is not None else None
        self.interactive = interactive
        self.immediate = immediate
        self.separator = separator
        self.intro = intro
        self.no_system_prompt = no_system_prompt

        self.api_adapter_name = api_adapter_name
        self.api_adapter_options = api_adapter_options or []
        self.api_adapter = get_api_adapter(
            self.api_adapter_name, parse_api_params(self.api_adapter_options)
        )

        self.messages = []

    @staticmethod
    def encode(obj: Any) -> dict[str, Any] | list[Any] | None:
        if hasattr(obj, "__iter__"):
            return list(obj)
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return None

    def log_json(self):
        if self.json_log_file:
            with open(self.json_log_file, "w", encoding="utf-8") as file:
                json.dump(self.messages, file, indent=2, default=self.encode)

    def get_completion(self) -> Tuple[Union[Iterable[str], None], Message]:
        return self.api_adapter.get_completion(self.messages)

    def get_separator(self) -> str:
        if self.separator is not None:
            return self.separator

        return "\n #" + ("=" * (get_terminal_size().columns - 4)) + "#\n"

    def add_chat_message(
        self,
        stream: Iterable[str] = None,
        message: Message = Message(),
        silent: bool = False,
    ) -> None:
        if not silent:
            print(f"{message.display_name}:\n")

            # if there is a stream, we have to sink the entire thing before we can be
            # sure the Message is complete
            if stream is not None:
                for chunk in stream:
                    print(chunk, end="", flush=True)
            else:
                print(message.content)

            print("\n" + self.get_separator())

        self.messages.append(message)

    @staticmethod
    def get_message_arg_content(arg_value: str) -> Tuple[str, str | None]:
        if not arg_value.startswith("@"):
            return (arg_value, None)

        if arg_value == "@-":
            return (sys.stdin.read(), "-")

        filename = normalize_path(arg_value[1:])

        if not os.path.exists(filename):
            return (None, filename)

        with open(filename, "r", encoding="utf-8") as file_handle:
            return (file_handle.read(), filename)

    # pylint: disable=too-many-branches
    def add_messages_from_args(self, args: list[str]) -> None:
        """
        Add messages from the command line arguments. Works in parallel with argparse, parsing the
        already-validated arguments. This is necessary to ensure that messages defined in command
        line arguments are added in the correct order.

        Args:
          args: The list of command line arguments (i.e. sys.argv[1:])

        Returns:
          None
        """
        silent = not self.interactive or not self.intro

        args_iter = iter(args)
        args_messages = []

        for arg in args_iter:
            if arg not in (
                "-s", "--system",
                "-a", "--assistant",
                "-u", "--user",
                "-f", "--file",
                "-i", "--image",
                "-c", "--conversation",
            ):
                continue

            arg_value = next(args_iter, None)
            (arg_value_parsed, arg_value_parsed_filename) = self.get_message_arg_content(arg_value)

            if arg in ("-c", "--conversation"):
                # so you can combine -c and -j on a file that doesn't exist yet
                if arg_value_parsed is None:
                    if arg_value_parsed_filename == self.json_log_file:
                        continue

                    raise ValueError(f"File {arg_value_parsed_filename} does not exist")

                conversation = json.loads(arg_value_parsed)
                for message in conversation:
                    args_messages.append(message_from_dict(message))
            elif arg_value_parsed is None and arg_value_parsed_filename is not None:
                raise ValueError(f"File {arg_value_parsed_filename} does not exist")
            elif arg in ("-s", "--system"):
                args_messages.append(Message(role="system", content=arg_value_parsed))
            elif arg in ("-a", "--assistant"):
                args_messages.append(Message(role="assistant", content=arg_value_parsed))
            elif arg in ("-u", "--user"):
                args_messages.append(Message(role="user", content=arg_value_parsed))
            elif arg in ("-f", "--file"):
                args_messages.append(FileMessage(role="user", file_path=arg_value_parsed))
            elif arg in ("-i", "--image"):
                args_messages.append(ImageMessage(role="user", image_path=arg_value_parsed))

        if not self.no_system_prompt and not any(
            message.role == "system" for message in args_messages
        ):
            args_messages.insert(0, Message(role="system", content=DEFAULT_SYSTEM_PROMPT))

        for message in args_messages:
            self.add_chat_message(message=message, silent=silent)

    def add_file(self) -> None:
        user_input = prompt("Enter file path: ")
        self.add_chat_message(message=Message(role="user", file_path=normalize_path(user_input)))

    def add_image(self) -> None:
        user_input = prompt("Enter image path: ")
        self.add_chat_message(message=Message(role="user", image_path=normalize_path(user_input)))

    def change_api_adapter_name(self) -> None:
        print("\nAvailable API Adapters:")

        adapter_list = get_adapter_list()

        for i, option in enumerate(adapter_list):
            print(f"[{i}] {option.HR_NAME or option.NAME}")
        user_input = prompt("\nEnter selection: ")

        try:
            choice = int(user_input)
        except ValueError:
            print(f"Invalid selection: {user_input}")
            return

        if choice < 0 or choice > len(self.api_adapter_options) + 1:
            print(f"Invalid selection: {choice}")
            return

        self.api_adapter_name = adapter_list[choice].NAME
        self.api_adapter = get_api_adapter(
            self.api_adapter_name, parse_api_params(self.api_adapter_options)
        )

    def change_api_adapter_options(self) -> None:
        while True:
            print("\nAPI Adapter Options:")
            print("[1] Add an option")

            for i, option in enumerate(self.api_adapter_options):
                print(f"[{i+2}] Remove {option}")

            user_input = prompt("\nEnter selection: ")

            if user_input == "":
                break

            try:
                choice = int(user_input)
            except ValueError:
                print(f"Invalid selection: {user_input}")
                continue

            if choice < 1 or choice > len(self.api_adapter_options) + 1:
                print(f"Invalid selection: {user_input}")
            elif choice == 1:
                user_input = prompt("\nEnter option (key=value): ")
                self.api_adapter_options.append(user_input)
            else:
                self.api_adapter_options.pop(choice - 2)

        self.api_adapter = get_api_adapter(
            self.api_adapter_name, parse_api_params(self.api_adapter_options)
        )

    def change_json_log_file(self) -> None:
        json_log_file = prompt(
            "Enter JSON log file path (leave blank to disable logging): ",
            default=self.json_log_file or "",
        )

        if json_log_file.strip() == "":
            self.json_log_file = None
        else:
            self.json_log_file = normalize_path(json_log_file)

        self.log_json()

    def menu(self) -> None:
        while True:
            opts = [
                ("Add a file", self.add_file),
                ("Add an image", self.add_image),
                ("Change API", self.change_api_adapter_name),
                ("Change API options", self.change_api_adapter_options),
                ("Change JSON log file", self.change_json_log_file),
            ]

            print("\nMenu:")
            for i, opt in enumerate(opts):
                print(f"[{i+1}] {opt[0]}")

            user_input = prompt("\nEnter selection: ")

            if user_input == "":
                break

            try:
                choice = int(user_input) - 1
            except ValueError:
                print(f"Invalid selection: {user_input}")
                continue

            if choice < 0 or choice >= len(opts):
                print(f"Invalid selection: {user_input}")
                continue

            try:
                opts[choice][1]()
            except Exception as ex:
                print(f"Error: {ex}")

    def repl(self, bindings: KeyBindings) -> None:
        default_input = None

        while True:
            print("User:\n")
            (user_input, user_input_type) = prompt(
                multiline=True, key_bindings=bindings, default=default_input or ""
            )
            default_input = None

            try:
                if user_input_type == "text":
                    if user_input != "":
                        self.add_chat_message(
                            message=Message(role="user", content=user_input),
                            silent=True,
                        )
                elif user_input_type == "menu":
                    self.menu()
                    default_input = user_input
                    continue
            except Exception as ex:
                print(f"Unable to add message: {str(ex)}\n")
                continue

            self.log_json()

            if user_input_type == "text":
                print(self.get_separator())

                try:
                    response_stream, response_message = self.get_completion()
                    self.add_chat_message(stream=response_stream, message=response_message)
                except Exception as ex:
                    print(f"Unable to get completion: {str(ex)}\n")
                    continue

                self.log_json()

    def main(self, args: list[str]) -> None:
        if self.interactive:
            print(f"{INTERACTIVE_KEYS}" + self.get_separator())

        self.add_messages_from_args(args)

        if not self.interactive:
            response_stream, response_message = self.get_completion()
            for fragment in response_stream:
                print(fragment, end="")
            self.add_chat_message(stream=response_stream, message=response_message, silent=True)
            self.log_json()
            return

        if self.immediate:
            response_stream, response_message = self.get_completion()
            self.add_chat_message(stream=response_stream, message=response_message)

        self.log_json()

        bindings = KeyBindings()
        bindings.add("c-c")(lambda _: sys.exit(0))
        bindings.add("c-d")(lambda _: sys.exit(0))
        bindings.add("enter")(lambda event: event.app.current_buffer.insert_text("\n"))
        bindings.add("escape", "enter")(
            lambda event: event.app.exit(result=(event.app.current_buffer.text, "text"))
        )
        bindings.add("c-b")(
            lambda event: event.app.exit(result=(event.app.current_buffer.text, "menu"))
        )

        self.repl(bindings)


###############
# INITIALIZER #
###############


def main():
    args = get_args()

    if args.help:
        print_help()
        return

    cli = LlmCli(
        log_file_json=args.log_file_json,
        interactive=not args.non_interactive,
        immediate=args.immediate,
        separator=args.separator,
        intro=not args.no_intro,
        no_system_prompt=args.no_system_prompt,
        api_adapter_name=args.api,
        api_adapter_options=args.api_options,
    )

    cli.main(sys.argv[1:])
