# Generated by Django 5.1 on 2024-09-04 16:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0004_alter_invitation_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="email_sent",
            field=models.BooleanField(default=False),
        ),
    ]