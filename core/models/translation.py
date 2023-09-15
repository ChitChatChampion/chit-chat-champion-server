from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class TranslationInput(models.Model):
    """
    Translation input
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    text = models.TextField(blank=False, max_length=5000)
    # TODO: inform FE
    context = models.CharField(max_length=1000)
    # TODO: change to entity
    languages = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class TranslationOutput(models.Model):
    """
    Translation output
    """

    # TODO: how to make sure at least one?
    input = models.ForeignKey(
        TranslationInput, on_delete=models.CASCADE, related_name="outputs"
    )
    text = models.TextField(blank=False, max_length=5000)
    # TODO: change to entity
    language = models.CharField(max_length=255)
    romanization = models.CharField(max_length=255)
    context = models.CharField(max_length=1000)
    meaning = models.CharField(max_length=1000)
    pronunciation_url = models.URLField(blank=True)
    # TODO: better way than json?
    pos = models.JSONField(blank=False, max_length=5000)

    def __str__(self):
        return self.text
