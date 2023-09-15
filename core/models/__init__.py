# https://www.webforefront.com/django/modelsoutsidemodels.html
# #:~:text=By%20default%2C%20Django%20models%20are,dozens%20or%20hundreds%20of%20models.
from .translation import TranslationInput, TranslationOutput
from .user import (
    User,
    UserConfig,
)


# https://github.com/django/django/blob/main/django/conf/urls/__init__.py
__all__ = [
    "TranslationInput",
    "TranslationOutput",
    "User",
    "UserConfig",
]
