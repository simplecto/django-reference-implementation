"""URL configuration for organizations app."""

from django.urls import path

from .views import create_organization, detail, index, invite

app_name = "organizations"

urlpatterns = [
    path("", index, name="index"),
    path("create/", create_organization, name="create_organization"),
    path("<slug:slug>/invite/", invite, name="invite"),
    path("<slug:slug>/", detail, name="detail"),
]
