import openai
import json
import uuid
from asgiref.sync import async_to_sync
from typing import Dict, List, Any, Optional, Callable

from core.models import TranslationInput
from .chatmanagers.utils import (
    OPENAI_MODEL,
    NONE,
    DETECT_LANGUAGE_CONFIG,
    POS_TAGGING_CONFIG,
)
from .chatmanagers import ChatMessage
from .chatmanagers.utils import extract_response_text
from .assistants import (
    TranslationAssistant,
    ContextAssistant,
    RomanizationAssistant,
)


# TODO: fix Any type
def join_texts(texts):
    if len(texts) < 1:
        return ""
    elif len(texts) == 1:
        return texts[0]

    texts_in_lower_case = [t.lower() for t in texts]

    # front_texts = texts_in_lower_case[:-1]
    # last_text = texts_in_lower_case[-1]

    # front_text = ", ".join(front_texts)
    # res = [front_text, last_text]

    # return " and ".join(res)

    text = ", ".join(texts_in_lower_case)

    return text


def join_languages(languages: List[str]) -> str:
    return ", ".join(languages)


def sanitize_nulls(texts: List[str]) -> List[str]:
    return [text for text in texts if text.strip().lower() != NONE]


def stream_translate_responses(
    num_translations: int,
    source_text: str,
    target_language: str,
    translation_assistant: TranslationAssistant,
    context_assistant: ContextAssistant,
    romanization_assistant: RomanizationAssistant,
    meaning_assistant: TranslationAssistant,
    input_instance: TranslationInput,
    on_progress: Optional[Callable[[Dict[str, Any]], None]],
):
    for i in range(num_translations):
        yield from stream_translate_response(
            i,
            source_text,
            target_language,
            translation_assistant,
            context_assistant,
            romanization_assistant,
            meaning_assistant,
            input_instance,
            on_progress,
        )


def format_response(item: Dict):
    return f"data: {json.dumps(item)}\n\n"


def stream_translate_response(
    index: int,
    source_text: str,
    target_language: str,
    translation_assistant: TranslationAssistant,
    context_assistant: ContextAssistant,
    romanization_assistant: RomanizationAssistant,
    meaning_assistant: TranslationAssistant,
    input_instance: TranslationInput,
    on_progress: Optional[Callable[[Dict[str, Any]], None]],
):
    translate_response = {
        "id": index,
        "text": "",
        "romanization": "",
        "context": "",
        "meaning": "",
        "language": target_language,
        "pronunciation_url": "",
        "pos": [],
    }

    def on_translation_progress(partial_response: ChatMessage):
        translate_response["text"] = partial_response.text.strip()
        yield format_response(translate_response)

    def on_context_progress(partial_response: ChatMessage):
        translate_response["context"] = partial_response.text.strip()
        yield format_response(translate_response)

    def on_romanization_progress(partial_response: ChatMessage):
        translate_response["romanization"] = partial_response.text.strip()
        yield format_response(translate_response)

    def on_meaning_progress(partial_response: ChatMessage):
        translate_response["meaning"] = partial_response.text.strip()
        yield format_response(translate_response)

    yield from translation_assistant.ask(source_text, on_translation_progress)
    yield from romanization_assistant.ask(
        translate_response["text"], on_romanization_progress
    )
    yield from context_assistant.ask(
        translate_response["text"], on_context_progress
    )
    yield from meaning_assistant.ask(
        translate_response["text"], on_meaning_progress
    )

    if on_progress:
        # TODO: better way?
        translate_response.pop("id")
        translation_output = {"input": input_instance, **translate_response}
        on_progress({"input": input_instance, **translation_output})


# TODO: extract into assistants classes


def get_pos_tagging_prompt(text: str) -> str:

    return f"""1) Extract all the proper nouns from the following text. The desired format is: <comma-separated list of proper nouns or '{NONE}'>
2) Extract all words from the following text, including the punctuations. The desired format is <comma-seperated list of word or '{NONE}'>
3) Consider proper nouns as one word and repeat step 2.
4) Convert into JSON list.

Text:
\"""
{text}
\"""

Step Number | Answer
--- | ---
1 |"""


def parse_pos_tagging_response(response_text: str) -> List[str]:

    lines = response_text.split("\n")
    line = lines[-1]
    values = line.split(" | ")
    value = values[-1]

    res = json.loads(value)
    return res


async def generate_pos_tagging_response(prompt: str) -> str:
    response: Any = openai.Completion.create(
        model=OPENAI_MODEL, prompt=prompt, **POS_TAGGING_CONFIG
    )

    return extract_response_text(response)


def get_language_key(key: str) -> str:

    table = {
        "Main Language": "main_language",
        "Other Languages": "other_languages",
        "Colloquial Languages": "colloquial_languages",
    }

    return table[key]


def get_detect_prompt(
    text: str,
) -> str:
    return f"""
List all languages and colloquial languages such as Singlish in the text in the format:
Main Language: 
Other Languages: 
Colloquial Languages: 

Text:
\"""
{text}
\"""

Main Language:"""


# TODO: refactor: config in .env
@async_to_sync
async def generate_detect_response(prompt: str) -> str:
    # you don't need to use await at the second line of the generate_detect_response function because the openai.Completion.create() function is already an asynchronous function. It returns an awaitable object that you can use to get the response asynchronously.
    response: Any = openai.Completion.create(
        model=OPENAI_MODEL, prompt=prompt, **DETECT_LANGUAGE_CONFIG
    )

    return extract_response_text(response)


def parse_detect_response(response_text: str) -> Dict[str, List[str]]:

    lines = response_text.splitlines()

    output_data: Dict[str, List[str]] = {}

    # TODO: refactor

    output_data["main_language"] = sanitize_nulls(lines[0].strip().split(", "))

    for i in range(1, len(lines)):
        line = lines[i]
        key, value = line.split(": ")
        languages = value.split(", ")

        output_data[get_language_key(key)] = sanitize_nulls(languages)

    return output_data
