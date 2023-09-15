from typing import Dict
from .assistant import Assistant


class RomanizationAssistant(Assistant):
    def __init__(self, target_language: str):
        name = "RomanizationGPT"
        prompt = f"You are {name} a {target_language} pronunciation assistant for English speaking people. I will provide a word or phrase in {target_language}, and you will provide its pronunciation in pinyin using the English alphabet. Your responses should only include the pronunciation, without any additional explanation or translation."

        super().__init__(prompt, name, persist=False)
