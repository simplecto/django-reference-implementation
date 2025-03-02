from allauth.mfa.adapter import get_adapter as get_mfa_adapter
from asgiref.sync import sync_to_async
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import sync_and_async_middleware

from myapp.models import SiteConfiguration


@sync_and_async_middleware
class Require2FAMiddleware:
    """Middleware to enforce 2FA for all users based on site configuration."""

    def __init__(self, get_response) -> None:  # noqa: ANN001, D107
        self.get_response = get_response

        # URLs that are always accessible without 2FA
        self.exempt_urls = [
            reverse("account_login"),
            reverse("account_logout"),
            reverse("account_email"),  # Email verification page
            "/admin/login/",  # Admin login
            "/static/",  # Static files
            "/media/",  # Media files
            "/accounts/",  # Alternative path for email verification
        ]

    def is_path_exempt(self, path: str) -> bool:
        """Check if the current path is exempt from 2FA enforcement.

        Args:
            path (str): The current path.

        Returns:
            bool: True if the path is exempt, False otherwise

        """
        return any(path.startswith(url) for url in self.exempt_urls)

    # Sync version
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and enforce 2FA if required."""
        if not request.user.is_authenticated or self.is_path_exempt(request.path):
            return self.get_response(request)

        # Check if 2FA is required by site configuration
        site_config = SiteConfiguration.objects.get()
        if not site_config.required_2fa:
            return self.get_response(request)

        mfa_adapter = get_mfa_adapter()
        has_2fa = mfa_adapter.is_mfa_enabled(request.user)

        # If 2FA is not enabled for this user, redirect to 2FA setup
        if not has_2fa:
            # Add a message explaining the redirect
            messages.warning(request, "Two-factor authentication is required. Please set it up now.")
            # Redirect to 2FA setup page
            return redirect("/accounts/2fa/")

        return self.get_response(request)

    # Async version
    async def __acall__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and enforce 2FA if required."""
        if not request.user.is_authenticated or self.is_path_exempt(request.path):
            return await self.get_response(request)

        # Check if 2FA is required by site configuration
        site_config = await sync_to_async(SiteConfiguration.objects.get)()
        if not site_config.required_2fa:
            return await self.get_response(request)

        mfa_adapter = get_mfa_adapter()
        # Properly await the async method
        has_2fa = await sync_to_async(mfa_adapter.is_mfa_enabled)(request.user)

        # If 2FA is not enabled for this user, redirect to 2FA setup
        if not has_2fa:
            # Add a message explaining the redirect
            await sync_to_async(messages.warning)(
                request, "Two-factor authentication is required. Please set it up now."
            )
            # Redirect to 2FA setup page
            return redirect("/accounts/2fa/")

        return await self.get_response(request)
