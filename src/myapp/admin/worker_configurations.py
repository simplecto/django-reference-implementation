from django.contrib import admin
from myapp.models import WorkerConfiguration


@admin.register(WorkerConfiguration)
class WorkerConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_enabled",
        "sleep_seconds",
        "log_level",
    )
    list_editable = (
        "is_enabled",
        "sleep_seconds",
        "log_level",
    )
