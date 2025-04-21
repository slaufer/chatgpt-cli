"""
This module provides message-related classes and utilities for handling
different types of messages, including text, file, and image messages.
"""

from llmcli.messages.message import Message
from llmcli.messages.file_message import FileMessage
from llmcli.messages.image_message import ImageMessage

__all__ = [
    "Message",
    "FileMessage",
    "ImageMessage"
]

def message_from_dict(data: dict) -> Message:
    """
    Create a message object from a dictionary representation.

    Parameters
    ----------
    data : dict
        A dictionary containing the message data. It must include a
        'message_type' key to determine the type of message.

    Returns
    -------
    Message
        An instance of `Message`, `FileMessage`, or `ImageMessage` depending
        on the 'message_type' in the input dictionary.
    """
    if data.get('message_type') == 'ImageMessage':
        return ImageMessage.from_dict(data)

    if data.get('message_type') == 'FileMessage':
        return FileMessage.from_dict(data)

    return Message.from_dict(data)
