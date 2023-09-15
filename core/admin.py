from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

# to convert string in python to human readable text
# so that it gets passed through the translation engine

from core import models


# UserAdmin to customize the model
admin.site.register(models.User)
admin.site.register(models.UserConfig)
admin.site.register(models.TranslationInput)
admin.site.register(models.TranslationOutput)
