"""File to register models in the admin panel."""

from django.contrib import admin
from myapp.models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin class for SiteConfiguration model."""

    pass
