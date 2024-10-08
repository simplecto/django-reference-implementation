# Generated by Django 5.1 on 2024-09-05 12:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0005_invitation_email_sent"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitation",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invitations_received",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="InvitationLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email_hash",
                    models.CharField(
                        editable=False,
                        help_text="SHA256 Hash of the email address.",
                        max_length=255,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("message", models.TextField(blank=True, default="", editable=False)),
                (
                    "organization",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitation_logs",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "invitation log",
                "verbose_name_plural": "invitation logs",
            },
        ),
    ]
