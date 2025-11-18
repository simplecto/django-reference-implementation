"""Tests for dataroom app."""

import os
import zipfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from require2fa.models import TwoFactorConfig

from .models import BulkDownload, Customer, DataEndpoint, FileDownload, UploadedFile

User = get_user_model()


class CustomerModelTests(TestCase):
    """Tests for Customer model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_customer_creation(self) -> None:
        """Test customer can be created."""
        customer = Customer.objects.create(
            name="Test Corp",
            notes="Test notes",
            created_by=self.user,
        )
        self.assertEqual(customer.name, "Test Corp")
        self.assertEqual(str(customer), "Test Corp")

    def test_customer_endpoints_relationship(self) -> None:
        """Test customer can have multiple endpoints."""
        customer = Customer.objects.create(name="Test Corp", created_by=self.user)
        endpoint1 = DataEndpoint.objects.create(
            customer=customer,
            name="Endpoint 1",
            created_by=self.user,
        )
        endpoint2 = DataEndpoint.objects.create(
            customer=customer,
            name="Endpoint 2",
            created_by=self.user,
        )
        self.assertEqual(customer.endpoints.count(), 2)


class DataEndpointModelTests(TestCase):
    """Tests for DataEndpoint model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.customer = Customer.objects.create(name="Test Corp", created_by=self.user)

    def test_endpoint_creation(self) -> None:
        """Test endpoint can be created."""
        endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Q1 POC",
            description="Test description",
            created_by=self.user,
        )
        self.assertEqual(endpoint.name, "Q1 POC")
        self.assertEqual(endpoint.status, DataEndpoint.STATUS_ACTIVE)
        self.assertIsNotNone(endpoint.id)  # UUID should be auto-generated

    def test_endpoint_str(self) -> None:
        """Test endpoint string representation."""
        endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test Endpoint",
            created_by=self.user,
        )
        expected = f"{self.customer.name} - Test Endpoint"
        self.assertEqual(str(endpoint), expected)

    def test_get_upload_url(self) -> None:
        """Test get_upload_url method."""
        endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test",
            created_by=self.user,
        )
        expected_url = f"/upload/{endpoint.id}/"
        self.assertEqual(endpoint.get_upload_url(), expected_url)


class UploadedFileModelTests(TestCase):
    """Tests for UploadedFile model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.customer = Customer.objects.create(name="Test Corp", created_by=self.user)
        self.endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test Endpoint",
            created_by=self.user,
        )

    def test_uploaded_file_creation(self) -> None:
        """Test file can be created."""
        uploaded_file = UploadedFile.objects.create(
            endpoint=self.endpoint,
            filename="test.txt",
            file_path="uploads/test/test.txt",
            file_size_bytes=1024,
            content_type="text/plain",
        )
        self.assertEqual(uploaded_file.filename, "test.txt")
        self.assertFalse(uploaded_file.is_deleted)

    def test_soft_delete(self) -> None:
        """Test soft delete functionality."""
        uploaded_file = UploadedFile.objects.create(
            endpoint=self.endpoint,
            filename="test.txt",
            file_path="uploads/test/test.txt",
            file_size_bytes=1024,
        )
        self.assertFalse(uploaded_file.is_deleted)

        # Soft delete
        uploaded_file.deleted_at = timezone.now()
        uploaded_file.save()
        self.assertTrue(uploaded_file.is_deleted)


class FileDownloadModelTests(TestCase):
    """Tests for FileDownload model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.customer = Customer.objects.create(name="Test Corp", created_by=self.user)
        self.endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test Endpoint",
            created_by=self.user,
        )
        self.uploaded_file = UploadedFile.objects.create(
            endpoint=self.endpoint,
            filename="test.txt",
            file_path="uploads/test/test.txt",
            file_size_bytes=1024,
        )

    def test_file_download_creation(self) -> None:
        """Test download log can be created."""
        download = FileDownload.objects.create(
            file=self.uploaded_file,
            downloaded_by=self.user,
            ip_address="127.0.0.1",
        )
        self.assertEqual(download.file, self.uploaded_file)
        self.assertEqual(download.downloaded_by, self.user)


class UploadViewTests(TestCase):
    """Tests for upload views."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.customer = Customer.objects.create(name="Test Corp", created_by=self.user)
        self.endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test Endpoint",
            created_by=self.user,
        )

    def test_upload_page_get(self) -> None:
        """Test upload page can be accessed."""
        url = reverse("dataroom:upload_page", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Endpoint")

    def test_upload_page_disabled_endpoint(self) -> None:
        """Test disabled endpoint shows correct message."""
        self.endpoint.status = DataEndpoint.STATUS_DISABLED
        self.endpoint.save()

        url = reverse("dataroom:upload_page", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload Disabled")

    def test_upload_page_archived_endpoint(self) -> None:
        """Test archived endpoint shows correct message."""
        self.endpoint.status = DataEndpoint.STATUS_ARCHIVED
        self.endpoint.save()

        url = reverse("dataroom:upload_page", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload Archived")

    def test_file_upload(self) -> None:
        """Test file can be uploaded via AJAX endpoint."""
        url = reverse("dataroom:ajax_upload", kwargs={"endpoint_id": self.endpoint.id})

        # Create a simple uploaded file
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

        response = self.client.post(url, {"file": uploaded_file})

        # Should return 201 Created with JSON response
        self.assertEqual(response.status_code, 201)

        # Check JSON response structure
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("file", response_data)
        self.assertEqual(response_data["file"]["filename"], "test.txt")
        self.assertIn("id", response_data["file"])
        self.assertIn("size", response_data["file"])
        self.assertIn("uploaded_at", response_data["file"])

        # Check file was created in database
        self.assertEqual(UploadedFile.objects.count(), 1)
        db_file = UploadedFile.objects.first()
        self.assertIsNotNone(db_file)
        self.assertEqual(db_file.endpoint, self.endpoint)
        self.assertEqual(db_file.filename, "test.txt")

        # Clean up created file
        if db_file:
            file_path = os.path.join(settings.MEDIA_ROOT, db_file.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_file_delete(self) -> None:
        """Test file can be deleted."""
        # Create a file
        uploaded_file = UploadedFile.objects.create(
            endpoint=self.endpoint,
            filename="test.txt",
            file_path="uploads/test/test.txt",
            file_size_bytes=1024,
        )

        url = reverse("dataroom:delete_file", kwargs={"endpoint_id": self.endpoint.id, "file_id": uploaded_file.id})
        response = self.client.post(url)

        # Should redirect after deletion
        self.assertEqual(response.status_code, 302)

        # Check file was soft deleted
        uploaded_file.refresh_from_db()
        self.assertTrue(uploaded_file.is_deleted)
        self.assertIsNotNone(uploaded_file.deleted_at)

    def test_ajax_upload_disabled_endpoint(self) -> None:
        """Test AJAX upload to disabled endpoint returns 403."""
        self.endpoint.status = DataEndpoint.STATUS_DISABLED
        self.endpoint.save()

        url = reverse("dataroom:ajax_upload", kwargs={"endpoint_id": self.endpoint.id})
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

        response = self.client.post(url, {"file": uploaded_file})

        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertIn("disabled", response_data["error"].lower())

    def test_ajax_upload_archived_endpoint(self) -> None:
        """Test AJAX upload to archived endpoint returns 403."""
        self.endpoint.status = DataEndpoint.STATUS_ARCHIVED
        self.endpoint.save()

        url = reverse("dataroom:ajax_upload", kwargs={"endpoint_id": self.endpoint.id})
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

        response = self.client.post(url, {"file": uploaded_file})

        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertIn("archived", response_data["error"].lower())

    def test_ajax_upload_no_file(self) -> None:
        """Test AJAX upload without file returns 400."""
        url = reverse("dataroom:ajax_upload", kwargs={"endpoint_id": self.endpoint.id})

        response = self.client.post(url, {})

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertIn("no file", response_data["error"].lower())

    def test_invalid_endpoint_404(self) -> None:
        """Test invalid endpoint returns 404."""
        import uuid

        url = reverse("dataroom:upload_page", kwargs={"endpoint_id": uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class BulkDownloadModelTests(TestCase):
    """Tests for BulkDownload model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.customer = Customer.objects.create(name="Test Corp", created_by=self.user)
        self.endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test Endpoint",
            created_by=self.user,
        )

    def test_bulk_download_creation(self) -> None:
        """Test bulk download log can be created."""
        bulk_download = BulkDownload.objects.create(
            endpoint=self.endpoint,
            downloaded_by=self.user,
            ip_address="127.0.0.1",
            file_count=5,
            total_bytes=5120,
        )
        self.assertEqual(bulk_download.endpoint, self.endpoint)
        self.assertEqual(bulk_download.downloaded_by, self.user)
        self.assertEqual(bulk_download.file_count, 5)
        self.assertEqual(bulk_download.total_bytes, 5120)


class BulkDownloadViewTests(TestCase):
    """Tests for bulk download functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        # Create TwoFactorConfig for middleware
        TwoFactorConfig.objects.create(required=False)

        self.client = Client()
        self.staff_user = User.objects.create_user(
            username="staffuser", email="staff@example.com", password="testpass123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="regularuser", email="regular@example.com", password="testpass123", is_staff=False
        )
        self.customer = Customer.objects.create(name="Test Corp", created_by=self.staff_user)
        self.endpoint = DataEndpoint.objects.create(
            customer=self.customer,
            name="Test Endpoint",
            created_by=self.staff_user,
        )

    def _create_test_file(self, filename: str, content: bytes) -> UploadedFile:
        """Helper method to create a test file."""
        # Create directory if it doesn't exist
        endpoint_dir = os.path.join(settings.MEDIA_ROOT, "uploads", str(self.endpoint.id))
        os.makedirs(endpoint_dir, exist_ok=True)

        # Write file to disk
        file_path = os.path.join(endpoint_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)

        # Create database record
        relative_path = os.path.join("uploads", str(self.endpoint.id), filename)
        uploaded_file = UploadedFile.objects.create(
            endpoint=self.endpoint,
            filename=filename,
            file_path=relative_path,
            file_size_bytes=len(content),
            content_type="text/plain",
        )
        return uploaded_file

    def tearDown(self) -> None:
        """Clean up test files."""
        # Clean up all test files
        endpoint_dir = os.path.join(settings.MEDIA_ROOT, "uploads", str(self.endpoint.id))
        if os.path.exists(endpoint_dir):
            for file in os.listdir(endpoint_dir):
                file_path = os.path.join(endpoint_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(endpoint_dir)

    def test_bulk_download_with_staff_user(self) -> None:
        """Test bulk download with staff user succeeds."""
        # Create test files
        file1 = self._create_test_file("test1.txt", b"Content 1")
        file2 = self._create_test_file("test2.txt", b"Content 2")
        file3 = self._create_test_file("test3.txt", b"Content 3")

        # Login as staff
        self.client.login(username="staffuser", password="testpass123")

        # Download zip
        url = reverse("dataroom:download_endpoint_zip", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn("attachment", response["Content-Disposition"])

        # Verify zip contents
        zip_content = BytesIO(b"".join(response.streaming_content) if hasattr(response, "streaming_content") else response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            names = zip_file.namelist()
            self.assertEqual(len(names), 3)
            self.assertIn("test1.txt", names)
            self.assertIn("test2.txt", names)
            self.assertIn("test3.txt", names)

            # Check file contents
            self.assertEqual(zip_file.read("test1.txt"), b"Content 1")
            self.assertEqual(zip_file.read("test2.txt"), b"Content 2")
            self.assertEqual(zip_file.read("test3.txt"), b"Content 3")

        # Verify audit logs
        self.assertEqual(BulkDownload.objects.count(), 1)
        bulk_download = BulkDownload.objects.first()
        self.assertIsNotNone(bulk_download)
        self.assertEqual(bulk_download.endpoint, self.endpoint)
        self.assertEqual(bulk_download.downloaded_by, self.staff_user)
        self.assertEqual(bulk_download.file_count, 3)

        # Verify individual file download logs
        self.assertEqual(FileDownload.objects.count(), 3)
        self.assertEqual(FileDownload.objects.filter(file=file1).count(), 1)
        self.assertEqual(FileDownload.objects.filter(file=file2).count(), 1)
        self.assertEqual(FileDownload.objects.filter(file=file3).count(), 1)

    def test_bulk_download_with_non_staff_user(self) -> None:
        """Test bulk download with non-staff user is denied."""
        # Create test file
        self._create_test_file("test.txt", b"Content")

        # Login as regular user
        self.client.login(username="regularuser", password="testpass123")

        # Try to download zip
        url = reverse("dataroom:download_endpoint_zip", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)

        # Should be denied
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Unauthorized", response.content)

        # No audit logs should be created
        self.assertEqual(BulkDownload.objects.count(), 0)
        self.assertEqual(FileDownload.objects.count(), 0)

    def test_bulk_download_with_anonymous_user(self) -> None:
        """Test bulk download with anonymous user redirects to login."""
        # Create test file
        self._create_test_file("test.txt", b"Content")

        # Try to download without logging in
        url = reverse("dataroom:download_endpoint_zip", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

        # No audit logs should be created
        self.assertEqual(BulkDownload.objects.count(), 0)
        self.assertEqual(FileDownload.objects.count(), 0)

    def test_bulk_download_empty_endpoint(self) -> None:
        """Test bulk download with no files redirects with message."""
        # Login as staff
        self.client.login(username="staffuser", password="testpass123")

        # Try to download zip from empty endpoint
        url = reverse("dataroom:download_endpoint_zip", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)

        # Should redirect back to upload page
        self.assertEqual(response.status_code, 302)

        # No audit logs should be created
        self.assertEqual(BulkDownload.objects.count(), 0)
        self.assertEqual(FileDownload.objects.count(), 0)

    def test_bulk_download_excludes_deleted_files(self) -> None:
        """Test bulk download excludes soft-deleted files."""
        # Create test files
        file1 = self._create_test_file("test1.txt", b"Content 1")
        file2 = self._create_test_file("test2.txt", b"Content 2")
        file3 = self._create_test_file("test3.txt", b"Content 3")

        # Soft delete one file
        file2.deleted_at = timezone.now()
        file2.save()

        # Login as staff
        self.client.login(username="staffuser", password="testpass123")

        # Download zip
        url = reverse("dataroom:download_endpoint_zip", kwargs={"endpoint_id": self.endpoint.id})
        response = self.client.get(url)

        # Check response
        self.assertEqual(response.status_code, 200)

        # Verify zip contents - should only have 2 files
        zip_content = BytesIO(b"".join(response.streaming_content) if hasattr(response, "streaming_content") else response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            names = zip_file.namelist()
            self.assertEqual(len(names), 2)
            self.assertIn("test1.txt", names)
            self.assertNotIn("test2.txt", names)  # Deleted file should be excluded
            self.assertIn("test3.txt", names)

        # Verify audit logs - should only count active files
        bulk_download = BulkDownload.objects.first()
        self.assertIsNotNone(bulk_download)
        self.assertEqual(bulk_download.file_count, 2)

        # Only 2 individual file downloads should be logged
        self.assertEqual(FileDownload.objects.count(), 2)
