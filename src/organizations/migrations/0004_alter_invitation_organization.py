# Generated by Django 5.1 on 2024-09-04 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0003_alter_invitation_invite_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitation",
            name="organization",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invitations",
                to="organizations.organization",
            ),
        ),
    ]
