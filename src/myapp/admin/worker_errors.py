from django.contrib import admin
from myapp.models import WorkerError


@admin.register(WorkerError)
class WorkerErrorAdmin(admin.ModelAdmin):
    list_display = (
        "worker",
        "created_at",
        "error_status",
    )
    list_filter = ("error_status",)
    search_fields = ("error",)
    readonly_fields = ("worker", "error", "created_at")
