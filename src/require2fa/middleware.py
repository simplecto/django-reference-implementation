"""2FA Enforcement Middleware.

SECURITY CRITICAL: This middleware enforces 2FA for authenticated users.
Previous versions used string prefix matching which allowed bypass via
any /accounts/* URL. This version uses proper Django URL resolution.

See GitHub Issue #173 for vulnerability details.
"""

import logging
from typing import TYPE_CHECKING

from allauth.mfa.adapter import get_adapter as get_mfa_adapter

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import Resolver404, resolve
from django.utils.decorators import sync_and_async_middleware

from .models import TwoFactorConfig

# Set up security logging
security_logger = logging.getLogger("security.2fa")


@sync_and_async_middleware
class Require2FAMiddleware:
    """Middleware to enforce 2FA for all users based on site configuration.

    Uses secure URL resolution instead of vulnerable string prefix matching.
    """

    def __init__(self, get_response) -> None:  # noqa: ANN001, D107
        self.get_response = get_response

        # URL names that are exempt from 2FA - Django's actual routing
        self.exempt_url_names = {
            "account_login",
            "account_logout",
            "account_email",  # Email management page - required for email verification
            "account_confirm_email",
            "account_email_verification_sent",
            "account_reset_password",
            "account_reset_password_done",
            "account_reset_password_from_key",
            "account_reset_password_from_key_done",
            "account_reauthenticate",  # Required for 2FA setup flow
            "mfa_activate_totp",  # TOTP activation - required to set up 2FA
            "mfa_deactivate_totp",  # TOTP deactivation
            "mfa_reauthenticate",  # MFA-specific reauthentication
            "mfa_generate_recovery_codes",  # Generate recovery codes
            "mfa_view_recovery_codes",  # View recovery codes
            "mfa_download_recovery_codes",  # Download recovery codes
        }

    def _is_static_request(self, request: HttpRequest) -> bool:
        """Check if this is a static file request using Django's settings."""
        static_url = getattr(settings, "STATIC_URL", "/static/")
        media_url = getattr(settings, "MEDIA_URL", "/media/")

        # SECURITY: Protect against dangerous root path configurations
        # that would bypass ALL 2FA security checks
        if static_url == "/" or media_url == "/":
            security_logger.error(
                "SECURITY MISCONFIGURATION: STATIC_URL or MEDIA_URL is set to root path '/'. "
                "This bypasses 2FA enforcement. Fix your Django settings."
            )
            # Don't treat root paths as static - force proper security checking
            return False

        return request.path.startswith((static_url, media_url))

    def _user_has_2fa(self, user: "AbstractUser") -> bool:
        """Check if user has 2FA enabled."""
        mfa_adapter = get_mfa_adapter()
        return mfa_adapter.is_mfa_enabled(user)

    def _is_exempt_url(self, request: HttpRequest) -> bool:
        """Check if current URL is exempt from 2FA by name."""
        # First try to get existing resolver_match
        resolver_match = getattr(request, "resolver_match", None)

        if not resolver_match:
            try:
                resolver_match = resolve(request.path_info)
            except Resolver404:
                # Can't resolve = probably 404 = let it through
                security_logger.debug("2FA: path %s doesn't resolve, allowing", request.path)
                return True
            except Exception as resolution_error:  # noqa: BLE001
                # Unexpected error during resolution - log and don't exempt
                security_logger.warning("2FA: error resolving path %s: %s", request.path, str(resolution_error))
                return False

        # Check by URL name
        if resolver_match.url_name in self.exempt_url_names:
            security_logger.debug("2FA exemption: URL name '%s' for %s", resolver_match.url_name, request.path)
            return True

        # Check namespaced URLs properly
        if resolver_match.namespace and resolver_match.url_name:
            namespaced_name = f"{resolver_match.namespace}:{resolver_match.url_name}"
            if namespaced_name in self.exempt_url_names:
                security_logger.debug("2FA exemption: namespaced URL '%s' for %s", namespaced_name, request.path)
                return True

        return False

    def _should_enforce_2fa(self, request: HttpRequest) -> bool:
        """Check if 2FA should be enforced for this request."""
        # Skip static/media files
        if self._is_static_request(request):
            return False

        # Skip if user not authenticated
        if not request.user.is_authenticated:
            return False

        # Skip exempt URLs
        if self._is_exempt_url(request):
            return False

        # Check if 2FA is required by site configuration
        config = TwoFactorConfig.objects.get()
        if not config.required:
            return False

        # Check if user has 2FA
        return not self._user_has_2fa(request.user)

    async def _should_enforce_2fa_async(self, request: HttpRequest) -> bool:
        """Async version: Check if 2FA should be enforced for this request."""
        # Skip static/media files
        if self._is_static_request(request):
            return False

        # Skip if user not authenticated
        if not request.user.is_authenticated:
            return False

        # Skip exempt URLs
        if self._is_exempt_url(request):
            return False

        # Check if 2FA is required by site configuration
        config = await sync_to_async(TwoFactorConfig.objects.get)()
        if not config.required:
            return False

        # Check if user has 2FA
        has_2fa = await sync_to_async(self._user_has_2fa)(request.user)
        return not has_2fa

    # Sync version
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and enforce 2FA if required."""
        if not self._should_enforce_2fa(request):
            return self.get_response(request)

        # User needs 2FA - log and redirect
        security_logger.warning(
            "2FA required but not configured for user: %s accessing: %s",
            getattr(request.user, "id", "unknown"),
            request.path,
        )

        # Don't redirect if we're already going to 2FA setup to avoid loops
        if not request.path.startswith("/accounts/2fa/"):
            messages.warning(request, "Two-factor authentication is required. Please set it up now.")
            return redirect("/accounts/2fa/")

        return self.get_response(request)

    # Async version
    async def __acall__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and enforce 2FA if required."""
        if not await self._should_enforce_2fa_async(request):
            return await self.get_response(request)

        # User needs 2FA - log and redirect
        await sync_to_async(security_logger.warning)(
            "2FA required but not configured for user: %s accessing: %s",
            getattr(request.user, "id", "unknown"),
            request.path,
        )

        # Don't redirect if we're already going to 2FA setup to avoid loops
        if not request.path.startswith("/accounts/2fa/"):
            await sync_to_async(messages.warning)(
                request, "Two-factor authentication is required. Please set it up now."
            )
            return redirect("/accounts/2fa/")

        return await self.get_response(request)
