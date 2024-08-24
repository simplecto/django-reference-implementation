"""Config URL Configuration."""

import django.views.generic
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import myapp.views

urlpatterns = [  # noqa: RUF005
    path(
        "robots.txt",
        django.views.generic.TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
        name="robots-txt",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", myapp.views.index, name="home"),
    path("health-check/", myapp.views.health_check, name="health-check"),
    path("profile/", myapp.views.profile, name="profile"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
