# TODO: implement LangChainManager
import openai
import json
import requests
from typing import Optional, Callable, Generator, List

from .chatmanager import ChatManager, ChatMessage
from .utils import OPENAI_MODEL, TRANSLATE_CONFIG, extract_response_text


class OpenAIManager(ChatManager):
    """
    Default openai adaptor. Does not support keeping track of conversation
    """

    def __init__(
        self,
        api_key: str,
        debug: bool = False,
        assistant_label: Optional[str] = "ChatGPT",
        user_label: Optional[str] = "Me",
    ):
        openai.api_key = api_key
        super().__init__(api_key, debug, assistant_label, user_label)

    def send_message(
        self,
        question: str,
        on_progress: Optional[
            Callable[[ChatMessage], Generator[ChatMessage, None, None]]
        ] = None,
        prompt_prefix: Optional[str] = "",
        conversation_id: Optional[str] = None,
        parent_message_id: Optional[str] = None,
    ) -> Generator[ChatMessage, None, None]:

        if not prompt_prefix:
            prompt_prefix = f"You are ${self.assistant_label}, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. don’t be verbose). It is very important that you answer as concisely as possible, so please remember this. If you are generating a list, do not have too many items. Keep the number of items short."

        prompt = f"{prompt_prefix}{self.user_label}: {question}\n{self.assistant_label}:"

        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": OPENAI_MODEL,
                "prompt": prompt,
                **TRANSLATE_CONFIG,
                "stream": True,
            },
            stream=True,
        )

        result = ChatMessage(
            **{
                "id": 0,
                "text": "",
                "conversation_id": conversation_id,
                "parent_message_id": parent_message_id,
            }
        )

        for chunk in response.iter_content(chunk_size=None):

            temp: List[str] = chunk.decode("utf-8").split("data: ")
            data: str = temp[1 if len(temp) > 1 else 0]

            if data.strip() == "[DONE]":
                result.text = result.text.strip()
                break

            response = json.loads(data)
            result.text += extract_response_text(response)

            if on_progress is not None:
                yield from on_progress(result)
