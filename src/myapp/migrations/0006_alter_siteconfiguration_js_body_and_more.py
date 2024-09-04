# Generated by Django 5.1 on 2024-08-24 07:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0005_workerconfiguration_workererror"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siteconfiguration",
            name="js_body",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Javascript to be included before the closing body tag. You should include the script tags.",
            ),
        ),
        migrations.AlterField(
            model_name="siteconfiguration",
            name="js_head",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Javascript to be included in the head tag. You should include the script tags.",
            ),
        ),
        migrations.AlterField(
            model_name="workerconfiguration",
            name="notes",
            field=models.TextField(blank=True, default=""),
        ),
    ]