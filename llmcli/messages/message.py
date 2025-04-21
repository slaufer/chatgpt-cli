"""
Module for handling messages in a conversation.

This module defines the `Message` class, which represents a message in a conversation.
It provides methods for serialization, deserialization, and comparison of messages.
"""

import json
from typing import Any

class Message:
    """
    Represents a message in a conversation.

    Parameters
    ----------
    message_type : str
        The type of the message, default is "Message".
    role : str | None
        The role of the sender (e.g., "user", "assistant").
    content : str | None
        The content of the message.
    display_name : str | None
        The display name of the sender.
    adapter : str | None
        The adapter which generated the message.
    adapter_options : dict[str, str] | None
        Options for the adapter.
    extra : dict[str, Any] | None
        Additional metadata for the message.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        role: str | None = "user",
        content: str | None = "",
        display_name: str | None = None,
        adapter: str | None = None,
        adapter_options: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,
        **_,
    ) -> None:
        self.message_type = "Message"
        self.role = role
        self.content = content
        self.adapter = adapter
        self.adapter_options = adapter_options
        self.display_name = display_name or role.capitalize()
        self.extra = extra

    def load_files(self) -> None:
        """
        Loads files for this message, if any.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
        raise NotImplementedError(f"load_files not implemented for {self.__class__.__name__}")

    def to_dict(self) -> dict:
        """
        Converts the message to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the message.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def to_json(self) -> str:
        """
        Converts the message to a JSON string.

        Returns
        -------
        str
            A JSON string representation of the message.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """
        Creates a Message instance from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary containing message attributes.

        Returns
        -------
        Message
            A Message instance created from the dictionary.
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """
        Creates a Message instance from a JSON string.

        Parameters
        ----------
        json_str : str
            A JSON string containing message attributes.

        Returns
        -------
        Message
            A Message instance created from the JSON string.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __eq__(self, other: "Message") -> bool:
        """
        Compares this message with another for equality.

        Parameters
        ----------
        other : Message
            The other message to compare.

        Returns
        -------
        bool
            True if the messages are equal, False otherwise.
        """
        if not isinstance(other, Message):
            return False

        return self.__dict__ == other.__dict__
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the message.

        Returns
        -------
        str
            A string representation of the message.
        """
        args = ', '.join(
            f'{k}={repr(v)}'
            for k, v in self.__dict__.items()
            if v is not None and k != 'message_type'
        )
        return f"{self.__class__.__name__}({args})"
