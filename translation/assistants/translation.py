from .assistant import Assistant


class TranslationAssistant(Assistant):
    def __init__(
        self,
        source_language: str,
        target_language: str,
        should_enable_variation: bool = True,
        context_text: str = "",
    ):
        name = f"{target_language} native"
        translationPrompt = f"You are {name}. I will speak to you in {source_language} and you will rewrite it in {target_language} as though it were originally written by a native {target_language} speaker. For the {target_language} text, {context_text}"

        super().__init__(translationPrompt, name, should_enable_variation)
