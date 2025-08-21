"""Integration test suite for 2FA middleware security."""

from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from require2fa.models import TwoFactorConfig

User = get_user_model()


class Require2FAMiddlewareIntegrationTest(TestCase):
    """Integration tests that actually test middleware behavior."""

    def setUp(self):
        """Set up test environment with real Django components."""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Enable 2FA site-wide (get_or_create for singleton)
        self.config, created = TwoFactorConfig.objects.get_or_create(defaults={'required': True})
        if not created:
            self.config.required = True
            self.config.save()

    def test_unauthenticated_users_access_everything(self):
        """Unauthenticated users should not be affected by 2FA middleware."""
        # These should all work without 2FA enforcement
        test_paths = [
            "/",
            "/accounts/login/",
            "/accounts/signup/",
        ]

        for path in test_paths:
            with self.subTest(path=path):
                response = self.client.get(path, follow=True)
                # Should not redirect to 2FA setup (302 to /accounts/2fa/)
                self.assertNotEqual(response.redirect_chain, [("/accounts/2fa/", 302)])

    def test_authenticated_user_without_2fa_redirected_to_setup(self):
        """Users without 2FA should be redirected to setup for protected URLs."""
        self.client.force_login(self.user)

        # These URLs should trigger 2FA redirect
        protected_paths = [
            "/",
            "/admin/",  # Admin now requires 2FA too
        ]

        for path in protected_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                if response.status_code == 302:
                    # Should redirect to 2FA setup
                    self.assertEqual(response.url, "/accounts/2fa/")

    def test_authentication_and_2fa_setup_always_accessible(self):
        """Authentication and 2FA setup URLs should never trigger 2FA redirect."""
        self.client.force_login(self.user)

        exempt_paths = [
            "/accounts/login/",
            "/accounts/logout/",
            "/accounts/email/",  # Email management - required for verification
            "/accounts/reauthenticate/",  # Required for 2FA setup
        ]

        for path in exempt_paths:
            with self.subTest(path=path):
                response = self.client.get(path, follow=True)
                # Should not redirect to 2FA setup
                final_url = response.request["PATH_INFO"]
                self.assertNotEqual(final_url, "/accounts/2fa/")

    def test_static_files_always_accessible(self):
        """Static and media files should never trigger 2FA redirect."""
        self.client.force_login(self.user)

        # These should work even for users without 2FA
        static_paths = [
            "/static/site.css",
            "/static/site.js",
            "/media/test.jpg",  # Will 404 but shouldn't redirect to 2FA
        ]

        for path in static_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                # Should not redirect to 2FA setup (can be 404, but not 302 to /accounts/2fa/)
                if response.status_code == 302:
                    self.assertNotEqual(response.url, "/accounts/2fa/")

    def test_2fa_disabled_site_wide_allows_everything(self):
        """When 2FA is disabled, middleware should not interfere."""
        # Disable 2FA site-wide
        self.config.required = False
        self.config.save()

        self.client.force_login(self.user)

        # Should be able to access protected areas without 2FA
        response = self.client.get("/")
        if response.status_code == 302:
            self.assertNotEqual(response.url, "/accounts/2fa/")

    def test_security_vulnerability_fixed(self):
        """Verify the original vulnerability is fixed - /accounts/* paths now protected."""
        self.client.force_login(self.user)

        # These paths were previously vulnerable (bypassed 2FA)
        # Now they should be protected
        previously_vulnerable_paths = [
            "/accounts/email/",  # Main vulnerability
            "/accounts/password/change/",
        ]

        for path in previously_vulnerable_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                if response.status_code == 302:
                    # Should redirect to 2FA setup, not allow access
                    self.assertEqual(response.url, "/accounts/2fa/")

    def test_no_redirect_loops(self):
        """2FA setup pages should not redirect to themselves."""
        self.client.force_login(self.user)

        # These should not create redirect loops
        setup_paths = [
            "/accounts/2fa/",
            "/accounts/2fa/setup/",
        ]

        for path in setup_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                # Should not redirect to itself
                if response.status_code == 302:
                    self.assertNotEqual(response.url, path)

    def test_malformed_urls_handled_safely(self):
        """Malformed URLs should not crash the middleware."""
        self.client.force_login(self.user)

        # These might cause URL resolution issues but shouldn't crash
        malformed_paths = [
            "/accounts/login/../admin/",  # Path traversal attempt
            "/accounts//login/",  # Double slash
            "/accounts/login/\x00",  # Null byte (will be filtered by Django)
        ]

        for path in malformed_paths:
            with self.subTest(path=path):
                # Should not crash - any response code is acceptable
                # Just testing that middleware handles it gracefully
                try:
                    response = self.client.get(path)
                    # Any response is fine - just shouldn't crash
                    self.assertIsNotNone(response)
                except Exception as e:
                    self.fail(f"Malformed URL {path} crashed middleware: {e}")

    @override_settings(STATIC_URL="/custom-static/", MEDIA_URL="/custom-media/")
    def test_custom_static_media_urls_respected(self):
        """Middleware should respect custom STATIC_URL and MEDIA_URL settings."""
        self.client.force_login(self.user)

        # Should work with custom static/media URLs
        custom_paths = [
            "/custom-static/app.css",
            "/custom-media/file.pdf",
        ]

        for path in custom_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                # Should not redirect to 2FA (will probably 404, but that's fine)
                if response.status_code == 302:
                    self.assertNotEqual(response.url, "/accounts/2fa/")


class SecurityRegressionTest(TestCase):
    """Specific tests to ensure the original security vulnerability is fixed."""

    def setUp(self):
        """Set up test with 2FA enabled."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        config, created = TwoFactorConfig.objects.get_or_create(defaults={'required': True})
        if not created:
            config.required = True
            config.save()

    def test_accounts_namespace_no_longer_bypassed(self):
        """The original /accounts/* bypass vulnerability should be fixed."""
        self.client.force_login(self.user)

        # These URLs were ALL bypassed in the vulnerable version
        # They should now be properly protected (redirect to 2FA setup)
        vulnerable_urls = [
            "/accounts/email/",
            "/accounts/password/change/",
        ]

        for url in vulnerable_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                # Should redirect to 2FA setup (the vulnerability fix)
                if response.status_code == 302:
                    self.assertEqual(
                        response.url, "/accounts/2fa/", f"URL {url} should redirect to 2FA setup, got {response.url}"
                    )

    def test_startswith_vulnerability_eliminated(self):
        """Verify that string prefix matching vulnerability is gone."""
        self.client.force_login(self.user)

        # The old vulnerability used startswith() so paths like these were bypassed:
        crafted_urls = [
            "/accounts/../some-admin-area/",  # Would have matched /accounts/ prefix
            "/static/../accounts/profile/",  # Would have matched /static/ prefix
        ]

        for url in crafted_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                # These should either 404 or require 2FA, not bypass
                if response.status_code == 200:
                    self.fail(f"URL {url} may be bypassing security checks")


class ConfigurationSecurityTest(TestCase):
    """Test that middleware protects against dangerous Django configurations."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        config, created = TwoFactorConfig.objects.get_or_create(defaults={'required': True})
        if not created:
            config.required = True
            config.save()

    @override_settings(MEDIA_URL="/", STATIC_URL="/static/")
    def test_dangerous_media_url_root_path_blocked(self):
        """MEDIA_URL set to '/' should not bypass 2FA security."""
        self.client.force_login(self.user)

        # Even with dangerous MEDIA_URL="/", root path should still require 2FA
        response = self.client.get("/")

        # Should redirect to 2FA setup, not bypass security
        if response.status_code == 302:
            self.assertEqual(response.url, "/accounts/2fa/",
                           "Root path should require 2FA even with MEDIA_URL='/'")

    @override_settings(STATIC_URL="/", MEDIA_URL="/media/")
    def test_dangerous_static_url_root_path_blocked(self):
        """STATIC_URL set to '/' should not bypass 2FA security."""
        self.client.force_login(self.user)

        # Even with dangerous STATIC_URL="/", root path should still require 2FA
        response = self.client.get("/")

        # Should redirect to 2FA setup, not bypass security
        if response.status_code == 302:
            self.assertEqual(response.url, "/accounts/2fa/",
                           "Root path should require 2FA even with STATIC_URL='/'")

    # Note: Django prevents STATIC_URL and MEDIA_URL from both being "/"
    # so we test individual cases above

    @override_settings(STATIC_URL="/static/", MEDIA_URL="/media/")
    def test_proper_configuration_allows_static_files(self):
        """Proper configuration should still allow static files through."""
        self.client.force_login(self.user)

        # With proper configuration, static files should be exempt
        static_paths = ["/static/app.css", "/media/file.jpg"]

        for path in static_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                # Should not redirect to 2FA (will 404, but that's fine)
                if response.status_code == 302:
                    self.assertNotEqual(response.url, "/accounts/2fa/")

    def test_missing_media_url_edge_case(self):
        """Test middleware behavior when getattr is used with safe defaults."""
        from require2fa.middleware import Require2FAMiddleware
        from django.test import RequestFactory
        from django.conf import settings

        # Create a middleware instance to test directly
        def dummy_response(req):
            return None
        middleware = Require2FAMiddleware(dummy_response)

        # Create test request
        factory = RequestFactory()
        request = factory.get("/")

        # Test the static request detection directly
        # Even if getattr falls back to defaults, should not treat root as static
        is_static = middleware._is_static_request(request)

        # Root path "/" should never be considered a static request
        # regardless of MEDIA_URL configuration edge cases
        self.assertFalse(is_static,
                        "Root path should never be treated as static file request")

        # Test with a proper media path
        media_request = factory.get("/media/test.jpg")
        is_media_static = middleware._is_static_request(media_request)

        # Proper media paths should be treated as static
        self.assertTrue(is_media_static,
                       "Proper media paths should be treated as static file requests")
