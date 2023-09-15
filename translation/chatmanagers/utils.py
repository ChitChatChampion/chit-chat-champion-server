import os

from typing import Dict, List


def extract_response_text(response: Dict[str, List[Dict[str, str]]]) -> str:
    return response["choices"][0]["text"]


NONE = "None"


# OXFORD
OXFORD_NATIVESAY_APP_ID: str = os.environ["OXFORD_NATIVESAY_APP_ID"]
OXFORD_APP_KEY: str = os.environ["OXFORD_APP_KEY"]

# OPENAI
OPENAI_MODEL = "text-davinci-003"
TRANSLATE_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0.6,
}
DETECT_LANGUAGE_CONFIG = {
    "temperature": 0.3,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}
POS_TAGGING_CONFIG = {
    "temperature": 0,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}
