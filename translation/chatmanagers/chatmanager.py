import json

from typing import Optional, Callable, Generator
from abc import ABC, abstractmethod
from typing import Optional


# TODO: add type hinting
# TODO: integrate with langchain here


class ChatMessage:
    def __init__(
        self,
        id: str,
        text: str,
        parent_message_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        # role: Role,
        # detail: Optional[Any] = None,
    ):
        self.id = id
        self.text = text
        self.parent_message_id = parent_message_id
        self.conversation_id = conversation_id
        # self.role = role
        # self.detail = detail

    def append(self, chunk):
        self.text += json.loads(chunk)


class ChatManager(ABC):
    @abstractmethod
    def __init__(
        self,
        api_key: str,
        debug: bool = False,
        assistant_label: Optional[str] = "AI",
        user_label: Optional[str] = "Me",
    ):
        self.api_key = api_key
        self.debug = debug
        self.assistant_label = assistant_label
        self.user_label = user_label

    @abstractmethod
    def send_message(
        self,
        question: str,
        on_progress: Optional[
            Callable[[ChatMessage], Optional[Generator]]
        ] = None,
        prompt_prefix: Optional[str] = "",
        conversation_id: Optional[str] = None,
        parent_message_id: Optional[str] = None,
    ) -> Generator[ChatMessage, None, None]:
        pass
