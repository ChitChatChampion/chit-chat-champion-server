from rest_framework import serializers

from core.models import TranslationInput, TranslationOutput


class TranslationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationOutput
        fields = (
            "text",
            "language",
            "romanization",
            "context",
            "meaning",
            "pronunciation_url",
            "pos",
        )


class TranslationInputSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    outputs = TranslationOutputSerializer(many=True, read_only=True)

    # TODO: output one more layer of translation output
    class Meta:
        model = TranslationInput
        fields = ("id", "text", "context", "languages", "outputs")
        read_only_fields = ("id", "text", "context", "languages")
