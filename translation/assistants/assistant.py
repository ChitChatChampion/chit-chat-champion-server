import os
from typing import Optional, Callable, Generator
from ..chatmanagers import ChatMessage, ChatManager, OpenAIManager


class Assistant:
    _api: ChatManager
    _description: Optional[str]
    _persist: bool
    _chat_message: Optional[ChatMessage] = None

    def __init__(
        self, description: str, name: str, persist: bool = True
    ) -> None:
        self._api = OpenAIManager(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            debug=True,
            assistant_label=name,
        )
        self._description = description
        self._persist = persist

    def ask(
        self,
        question: str,
        on_progress: Optional[
            Callable[[ChatMessage], Optional[Generator]]
        ] = None,
    ):
        if not question:
            raise ValueError("Question should not be empty")

        prompt_prefix = (
            f"{self._description}\n\n"
            if not self._chat_message
            else self._description
        )

        yield from self._api.send_message(
            question,
            on_progress=on_progress,
            prompt_prefix=prompt_prefix,
            conversation_id=self._chat_message.conversation_id
            if self._chat_message
            else None,
            parent_message_id=self._chat_message.id
            if self._chat_message
            else None,
        )
