"""Basic views for myapp."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .profile import profile


def index(request: HttpRequest) -> HttpResponse:
    """Show the homepage.

    :param request:
    :return:
    """
    test_flash = request.GET.get("test_flash", None)
    if test_flash:
        messages.success(request, "This is a test flash message.")

    return render(request, "home.html")


def health_check(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    """Tell the load balancer or Docker to check if the server is up.

    :return:
    """
    return HttpResponse("OK")


__all__ = [
    "profile",
]
