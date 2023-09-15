import os

from decouple import config

from api.settings.common import *


SECRET_KEY = config("SECRET_KEY", default="")
if not SECRET_KEY:
    with open(os.path.join(BASE_DIR, "secret_key.txt")) as f:
        SECRET_KEY = f.read().strip()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "api", "127.0.0.1"]


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
