"""Basic views for myapp."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def index(request: HttpRequest) -> HttpResponse:
    """Redirect to login page.

    :param request:
    :return:
    """
    return redirect("/accounts/login/")


def health_check(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    """Tell the load balancer or Docker to check if the server is up.

    :return:
    """
    return HttpResponse(b"OK")
