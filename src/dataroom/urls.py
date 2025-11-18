"""URL configuration for dataroom app."""

from django.urls import path

from . import views

app_name = "dataroom"

urlpatterns = [
    path("upload/<uuid:endpoint_id>/", views.upload_page, name="upload_page"),
    path("upload/<uuid:endpoint_id>/ajax/", views.ajax_upload, name="ajax_upload"),
    path("upload/<uuid:endpoint_id>/delete/<int:file_id>/", views.delete_file, name="delete_file"),
    path("upload/<uuid:endpoint_id>/download-zip/", views.download_endpoint_zip, name="download_endpoint_zip"),
]
