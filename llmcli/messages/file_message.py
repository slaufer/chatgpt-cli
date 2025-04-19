from llmcli.messages.message import Message
from llmcli.util import normalize_path

class FileMessage(Message):
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
        if self.file_path is None:
            return

        self.file_path = normalize_path(self.file_path)

        if self.file_content is None:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.file_content = file.read()

        self.content = f"### File: {self.file_path} (contents hidden)"
