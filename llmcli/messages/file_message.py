"""
Module for handling file-based messages in a conversation.

This module defines the `FileMessage` class, which represents a message containing
file content. It provides functionality to load file content and manage metadata
related to the file.
"""

from llmcli.messages.message import Message
from llmcli.util import normalize_path

class FileMessage(Message):
    """
    Represents a message containing file content.

    Parameters
    ----------
    file_content : str | None
        The content of the file.
    file_path : str | None
        The path to the file.
    """

    def __init__(
        self,
        file_content: str = None,
        file_path: str = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.message_type = "FileMessage"
        self.file_content = file_content
        self.file_path = file_path
        self.load_files()

    def load_files(self) -> None:
        """
        Loads the file content if a file path is provided.

        If `file_path` is specified, the file is read, and its content is stored
        in `file_content`. The `content` attribute is updated to indicate that
        the file content is hidden.

        Raises
        ------
        FileNotFoundError
            If the file at `file_path` does not exist.
        """
        if self.file_path is None:
            return

        self.file_path = normalize_path(self.file_path)

        if self.file_content is None:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.file_content = file.read()

        self.content = f"### File: {self.file_path} (contents hidden)"
