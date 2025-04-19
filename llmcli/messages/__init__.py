from llmcli.messages.message import Message
from llmcli.messages.file_message import FileMessage
from llmcli.messages.image_message import ImageMessage

__all__ = [
    "Message",
    "FileMessage",
    "ImageMessage"
]

def message_from_dict(data: dict) -> Message:
    if data.get('message_type') == 'ImageMessage':
        return ImageMessage.from_dict(data)

    if data.get('message_type') == 'FileMessage':
        return FileMessage.from_dict(data)

    return Message.from_dict(data)
    