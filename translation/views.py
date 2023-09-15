import openai
import os
import requests
from typing import List, Dict, Any

from django.db.models import QuerySet
from django.http import StreamingHttpResponse

from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import TranslationInput, TranslationOutput, UserConfig
from .serializers import (
    TranslationInputSerializer,
)
from .chatmanagers.utils import (
    OXFORD_NATIVESAY_APP_ID,
    OXFORD_APP_KEY,
)
from .utils import (
    get_detect_prompt,
    generate_detect_response,
    parse_detect_response,
    stream_translate_responses,
    join_texts,
    join_languages,
)


from .assistants import (
    ContextAssistant,
    TranslationAssistant,
    RomanizationAssistant,
)


openai.api_key = os.environ["OPENAI_API_KEY"]


class BaseTranslationAttrViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    """Base viewset for user owned translation attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        queryset: QuerySet = self.queryset or QuerySet()
        return (
            queryset.filter(user=self.request.user).order_by("-id").distinct()
        )


class TranslationViewSet(BaseTranslationAttrViewSet):
    """Manage tags in the database"""

    queryset = TranslationInput.objects.all()
    serializer_class = TranslationInputSerializer

    @action(detail=False, methods=["delete"])
    def clear_history(self, request):
        TranslationInput.objects.filter(user=self.request.user).delete()
        return Response(status=204)

    @action(detail=False, methods=["post"])
    def detect_language(self, request):

        text = request.data.get("text")

        prompt = get_detect_prompt(text)

        response_text = generate_detect_response(prompt)

        res = parse_detect_response(response_text)

        return Response(
            res,
            status=status.HTTP_200_OK,
        )

    # TODO: refactor
    @action(methods=["post"], detail=False)
    def search(self, request):
        text = request.data.get("text")
        try:
            # TODO: change target language
            target_language = "en-us"

            # Make the API call here
            response = requests.get(
                f"https://od-api.oxforddictionaries.com/api/v2/entries/{target_language}/{text}",
                headers={
                    "app_id": OXFORD_NATIVESAY_APP_ID,
                    "app_key": OXFORD_APP_KEY,
                },
            )
            # Check if the word is valid
            if response.status_code == 404:
                return Response(
                    {"error": "word not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            data = response.json()

            defs = []
            for sense in data["results"][0]["lexicalEntries"][0]["entries"][0][
                "senses"
            ]:
                word_class = ""
                if "grammaticalFeatures" in sense:
                    word_class = sense["grammaticalFeatures"][0]["text"]

                definition = sense["definitions"][0]
                defs.append(
                    {"definition": definition, "word_class": word_class}
                )

            return Response({"definitions": defs}, status=status.HTTP_200_OK)

        except:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def translate(self, request):

        user_config = UserConfig.objects.get(user=request.user)
        num_translations = user_config.alternative_translations_count

        data = request.data
        source_text = data.get("text", "")
        languages: List[str] = data.get("languages", [])
        contexts: List[str] = data.get("contexts", [])
        target_language = data.get("target_language", "")

        if len(languages) < 1:
            return Response(
                {"error": "Languages are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        source_language = languages[0]
        context = join_texts(contexts)

        translation_assistant = TranslationAssistant(
            source_language=source_language,
            target_language=target_language,
            should_enable_variation=True,
            context_text=context,
        )
        context_assistant = ContextAssistant(source_language=source_language)
        romanization_assistant = RomanizationAssistant(
            target_language=target_language
        )
        meaning_assistant = TranslationAssistant(
            source_language=target_language,
            target_language=source_language,
            should_enable_variation=False,
        )

        input_data = {
            "user": request.user,
            "text": source_text,
            "context": context,
            "languages": join_languages(languages),
        }

        # TODO: change to serializer
        # TODO: dont commit first
        input_instance = TranslationInput.objects.create(**input_data)

        def on_progress(translation: Dict[str, Any]):
            TranslationOutput.objects.create(**translation)

        response = StreamingHttpResponse(
            stream_translate_responses(
                num_translations,
                source_text,
                target_language,
                translation_assistant,
                context_assistant,
                romanization_assistant,
                meaning_assistant,
                input_instance,
                on_progress,
            ),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"

        return response
