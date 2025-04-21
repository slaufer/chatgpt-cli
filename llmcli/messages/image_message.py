"""
Module for handling image-based messages in a conversation.

This module defines the `ImageMessage` class, which represents a message containing
image content. It provides functionality to load image content, encode it in base64,
and manage metadata such as the MIME type of the image.
"""
import base64
from llmcli.messages.message import Message
from llmcli.util import get_mime_type, normalize_path

class ImageMessage(Message):
    """
    Represents a message containing image content.

    Parameters
    ----------
    image_path : str | None
        The path to the image file.
    image_content : str | None
        The base64-encoded content of the image.
    image_type : str | None
        The MIME type of the image.
    """

    def __init__(
        self,
        image_path: str = None,
        image_content: str = None,
        image_type: str = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.message_type = "ImageMessage"
        self.image_path = image_path
        self.image_content = image_content
        self.image_type = image_type
        self.load_files()

    def load_files(self) -> None:
        """
        Loads the image content and MIME type if an image path is provided.

        If `image_path` is specified, the image is read, and its content is
        base64-encoded and stored in `image_content`. The MIME type is
        determined and stored in `image_type`. The `content` attribute is
        updated to indicate that the image content is hidden.

        Raises
        ------
        FileNotFoundError
            If the image file at `image_path` does not exist.
        """
        if self.image_path is None:
            return

        self.image_path = normalize_path(self.image_path)

        if self.image_content is None:
            with open(self.image_path, "rb") as file:
                self.image_content = base64.b64encode(file.read()).decode("utf-8")

        if self.image_type is None:
            self.image_type = get_mime_type(self.image_path) or "image/jpeg"

        self.content = f"### Image: {self.image_path} ({self.image_type}) (contents hidden)"
