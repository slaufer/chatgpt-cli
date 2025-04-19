"""
A class representing a message in the conversation.
"""
import json

class Message:
    """
    A class representing a message in the conversation.
    """
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        role="user",
        content="",
        adapter=None,
        adapter_options=None,
        display_name=None,
        extra=None,
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
        raise NotImplementedError(f"load_files not implemented for {self.__class__.__name__}")

    def to_dict(self) -> dict:
        """
        Converts the message to a dictionary.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def to_json(self) -> str:
        """
        Converts the message to a JSON string.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """
        Converts a dictionary to a Message object.
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """
        Converts a JSON string to a Message object.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __eq__(self, other: "Message") -> bool:
        if not isinstance(other, Message):
            return False

        return self.__dict__ == other.__dict__
