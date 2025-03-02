# Generated by Django 5.1.6 on 2025-03-02 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_siteconfiguration_js_body_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='required_2fa',
            field=models.BooleanField(default=False, help_text='Require 2FA for all users.'),
        ),
    ]
