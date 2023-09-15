import os

from api.settings.common import *

# TODO: fix F401, F403, F405

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = ["api", "api.nativesay.com"]

# HTTPS settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# TODO: configure HTTPS for Elastic Beanstalk environment
# SECURE_SSL_REDIRECT = True

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# AWS_STORAGE_BUCKET_NAME = "digitalace"
# AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME

CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = [
#     "http://eizea.com",
#     "http://www.eizea.com",
#     "https://eizea.com",
#     "https://www.eizea.com",
#     "http://digitalace-env.eba-jj7vp4ec.us-east-2.elasticbeanstalk.com",
#     "http://localhost:3000",
#     "http://eizea.com/",
#     "http://www.eizea.com/",
#     "https://eizea.com/",
#     "https://www.eizea.com/",
#     "http://digitalace-env.eba-jj7vp4ec.us-east-2.elasticbeanstalk.com/",
#     "http://localhost:3000/",
# ]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("PGHOST"),
        "NAME": os.environ.get("PGDATABASE"),
        "USER": os.environ.get("PGUSER"),
        "PASSWORD": os.environ.get("PGPASSWORD"),
        "PORT": os.environ.get("PGPORT"),
    }
}
