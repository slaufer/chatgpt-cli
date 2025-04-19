import base64
from llmcli.messages.message import Message
from llmcli.util import get_mime_type, normalize_path

class ImageMessage(Message):
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
        if self.image_path is None:
            return

        self.image_path = normalize_path(self.image_path)

        if self.image_content is None:
            with open(self.image_path, "rb") as file:
                self.image_content = base64.b64encode(file.read()).decode("utf-8")

        if self.image_type is None:
            self.image_type = get_mime_type(self.image_path) or "image/jpeg"

        self.content = f"### Image: {self.image_path} ({self.image_type}) (contents hidden)"
