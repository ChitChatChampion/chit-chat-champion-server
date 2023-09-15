# Generated by Django 4.1.5 on 2023-01-14 07:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_groups_user_is_superuser_user_user_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='translationinput',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
