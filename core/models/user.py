import uuid
import os
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):

        """Creates and save a new user"""
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        UserConfig.objects.create(user=user)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    """Custom user model that supports using email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class UserConfig(models.Model):
    """User configuration"""

    class SpeechGender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    class RepeatSpeechCount(models.TextChoices):
        ONE = "one", _("one")
        THREE = "three", _("three")
        FIVE = "five", _("five")
        NINE = "nine", _("nine")

    class RepeatSpeed(models.TextChoices):
        VERY_SLOW = "very_slow", _("very_slow")
        SLOW = "slow", _("slow")
        NORMAL = "normal", _("normal")
        FAST = "fast", _("fast")

    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
    )
    # TODO: set a range
    repeat_speech_count = models.CharField(
        max_length=255,
        blank=False,
        choices=RepeatSpeechCount.choices,
        default=RepeatSpeechCount.ONE,
    )
    speech_speed = models.CharField(
        max_length=255,
        blank=False,
        choices=RepeatSpeed.choices,
        default=RepeatSpeed.NORMAL,
    )
    speech_gender = models.CharField(
        max_length=255,
        blank=False,
        choices=SpeechGender.choices,
        default=SpeechGender.FEMALE,
    )
    is_editor_mode = models.BooleanField(default=True)
    alternative_translations_count = models.IntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Theme(models.TextChoices):
        LIGHT = "light", _("light")
        DARK = "dark", _("dark")

    class Language(models.TextChoices):
        ENGLISH = "en", _("en")
        MANDARIN = "zh", _("zh")

    theme = models.CharField(
        max_length=255,
        blank=True,
        default=Theme.LIGHT,
        choices=Theme.choices,
    )
    language = models.CharField(
        max_length=255,
        blank=True,
        default=Language.ENGLISH,
        choices=Language.choices,
    )

    def __str__(self):
        return self.user.email

    def delete(self, using=None, keep_parents=False):
        # https://stackoverflow.com/questions/19182001/how-to-protect-objects-from-deletion-in-django
        raise AssertionError(
            "%s object can't be deleted." % (self._meta.object_name,)
        )
