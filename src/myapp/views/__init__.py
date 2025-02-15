"""Basic views for myapp."""

from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Show the homepage.

    :param request:
    :return:
    """
    test_flash = request.GET.get("test_flash", None)
    if test_flash:
        messages.success(request, "This is a test flash message.")

    return render(request, "myapp/home.html")


def health_check(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    """Tell the load balancer or Docker to check if the server is up.

    :return:
    """
    return HttpResponse(b"OK")


@login_required
def my_profile(request: HttpRequest) -> HttpResponse:
    """Profile page view. This page shows the user's profile information.

    :param request:
    :return:
    """
    # pylint: disable=no-member
    social_accounts = SocialAccount.objects.all()

    return render(
        request,
        "account/profile.html",
        {
            "social_accounts": social_accounts,
        },
    )
