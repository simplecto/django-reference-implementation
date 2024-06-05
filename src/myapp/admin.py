"""File to register models in the admin panel."""

from django.contrib import admin
from myapp.models import SiteConfiguration


admin.site.register(SiteConfiguration)
