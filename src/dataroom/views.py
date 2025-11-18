"""Views for the dataroom app."""

import io
import os
import re
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import BulkDownload, DataEndpoint, FileDownload, UploadedFile


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks."""
    # Remove any path components
    filename = os.path.basename(filename)

    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    filename = re.sub(r"[^\w\.\-]", "_", filename)

    # Prevent hidden files and relative paths
    filename = filename.lstrip(".")

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    # Limit filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext

    return filename


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR", "")


def get_unique_filepath(endpoint_id: str, filename: str) -> tuple[str, str]:
    """Generate unique file path to prevent overwrites."""
    # Sanitize filename
    clean_filename = sanitize_filename(filename)

    # Create endpoint-specific directory
    endpoint_dir = os.path.join("uploads", str(endpoint_id))
    full_dir = os.path.join(settings.MEDIA_ROOT, endpoint_dir)

    # Create directory if it doesn't exist
    Path(full_dir).mkdir(parents=True, exist_ok=True)

    # Check if file exists, add timestamp if needed
    name, ext = os.path.splitext(clean_filename)
    counter = 1
    test_filename = clean_filename
    test_path = os.path.join(full_dir, test_filename)

    while os.path.exists(test_path):
        # Add timestamp and counter
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_filename = f"{name}-{timestamp}-{counter}{ext}"
        test_path = os.path.join(full_dir, test_filename)
        counter += 1

    # Return relative path and final filename
    relative_path = os.path.join(endpoint_dir, test_filename)
    return relative_path, test_filename


@require_http_methods(["GET"])
def upload_page(request: HttpRequest, endpoint_id: str) -> HttpResponse:
    """Display upload page for a specific endpoint."""
    # Get endpoint or 404
    endpoint = get_object_or_404(DataEndpoint, id=endpoint_id)

    # Check if endpoint is active
    if endpoint.status == DataEndpoint.STATUS_DISABLED:
        return render(
            request,
            "dataroom/upload_disabled.html",
            {"endpoint": endpoint},
        )

    if endpoint.status == DataEndpoint.STATUS_ARCHIVED:
        return render(
            request,
            "dataroom/upload_archived.html",
            {"endpoint": endpoint},
        )

    # Show upload form and file list
    # Get all non-deleted files for this endpoint
    files = endpoint.files.filter(deleted_at__isnull=True).order_by("-uploaded_at")

    context = {
        "endpoint": endpoint,
        "files": files,
        "customer_name": endpoint.customer.name,
    }

    return render(request, "dataroom/upload_page.html", context)


@require_http_methods(["POST"])
def delete_file(request: HttpRequest, endpoint_id: str, file_id: int) -> HttpResponse:
    """Handle file deletion request from customer."""
    # Get endpoint or 404
    endpoint = get_object_or_404(DataEndpoint, id=endpoint_id)

    # Get file or 404
    uploaded_file = get_object_or_404(UploadedFile, id=file_id, endpoint=endpoint)

    # Check if already deleted
    if uploaded_file.is_deleted:
        messages.warning(request, "File is already deleted.")
        return redirect("dataroom:upload_page", endpoint_id=endpoint.id)

    # Soft delete the file
    uploaded_file.deleted_at = timezone.now()
    uploaded_file.deleted_by_ip = get_client_ip(request)
    uploaded_file.save()

    messages.success(request, f"File '{uploaded_file.filename}' has been deleted.")

    return redirect("dataroom:upload_page", endpoint_id=endpoint.id)


@require_http_methods(["POST"])
def ajax_upload(request: HttpRequest, endpoint_id: str) -> JsonResponse:
    """Handle AJAX file upload from Uppy."""
    try:
        # Get endpoint or 404
        endpoint = get_object_or_404(DataEndpoint, id=endpoint_id)

        # Check if endpoint is active
        if endpoint.status == DataEndpoint.STATUS_DISABLED:
            return JsonResponse({"error": "This upload endpoint is disabled."}, status=403)

        if endpoint.status == DataEndpoint.STATUS_ARCHIVED:
            return JsonResponse({"error": "This upload endpoint is archived."}, status=403)

        # Check if file was uploaded
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file was uploaded."}, status=400)

        uploaded_file = request.FILES["file"]

        # Validate file
        if not uploaded_file.name:
            return JsonResponse({"error": "Invalid file."}, status=400)

        # Get unique file path
        relative_path, final_filename = get_unique_filepath(str(endpoint.id), uploaded_file.name)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        # Save file to disk
        with open(full_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Get file size
        file_size = os.path.getsize(full_path)

        # Get client IP
        client_ip = get_client_ip(request)

        # Create database record
        file_record = UploadedFile.objects.create(
            endpoint=endpoint,
            filename=final_filename,
            file_path=relative_path,
            file_size_bytes=file_size,
            content_type=uploaded_file.content_type or "",
            uploaded_by_ip=client_ip,
        )

        # Return success response with file details
        return JsonResponse(
            {
                "success": True,
                "file": {
                    "id": file_record.id,
                    "filename": file_record.filename,
                    "size": file_record.file_size_bytes,
                    "uploaded_at": file_record.uploaded_at.isoformat(),
                },
            },
            status=201,
        )

    except Exception as e:
        # Clean up file if it was saved
        if "full_path" in locals() and os.path.exists(full_path):
            os.remove(full_path)

        return JsonResponse({"error": f"Error uploading file: {e!s}"}, status=500)


@login_required
@require_http_methods(["GET"])
def download_endpoint_zip(request: HttpRequest, endpoint_id: str) -> HttpResponse:
    """Download all files from an endpoint as a zip file (staff only)."""
    # Verify user is staff
    if not request.user.is_staff:
        return HttpResponse("Unauthorized: Staff access required", status=403)

    # Get endpoint or 404
    endpoint = get_object_or_404(DataEndpoint, id=endpoint_id)

    # Get all non-deleted files for this endpoint
    files = endpoint.files.filter(deleted_at__isnull=True).order_by("filename")

    # Check if there are any files to download
    if not files.exists():
        messages.warning(request, "No files available to download.")
        return redirect("dataroom:upload_page", endpoint_id=endpoint.id)

    # Get client IP
    client_ip = get_client_ip(request)

    # Calculate total size
    total_bytes = sum(f.file_size_bytes for f in files)

    # Create zip filename
    # Format: {customer-name}-{endpoint-name}-YYYY-MM-DD-HHMMSS.zip
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    customer_name_clean = re.sub(r"[^\w\-]", "_", endpoint.customer.name)
    endpoint_name_clean = re.sub(r"[^\w\-]", "_", endpoint.name)
    zip_filename = f"{customer_name_clean}-{endpoint_name_clean}-{timestamp}.zip"

    # Create in-memory buffer for zip file
    buffer = io.BytesIO()

    # Create zip file
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for uploaded_file in files:
            # Construct full file path
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file_path)

            # Check if file exists on disk
            if os.path.exists(file_path):
                # Add file to zip with original filename
                zip_file.write(file_path, uploaded_file.filename)

                # Create individual FileDownload audit record
                FileDownload.objects.create(
                    file=uploaded_file,
                    downloaded_by=request.user,
                    ip_address=client_ip,
                )

    # Create BulkDownload audit record
    BulkDownload.objects.create(
        endpoint=endpoint,
        downloaded_by=request.user,
        ip_address=client_ip,
        file_count=files.count(),
        total_bytes=total_bytes,
    )

    # Get zip content
    zip_content = buffer.getvalue()

    # Create response
    response = HttpResponse(zip_content, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
    response["Content-Length"] = len(zip_content)

    return response
