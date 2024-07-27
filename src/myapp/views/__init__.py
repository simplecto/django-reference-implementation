from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .profile import profile


def index(request: HttpRequest) -> HttpResponse:
    """
    Home page view. This is the first page that the user sees when they visit
    the site
    :param request:
    :return:
    """
    return render(request, "home.html")


def health_check(request) -> HttpResponse:
    """
    Health check view. Used by the load balancer or Docker to check if the
    server is up
    :return:
    """
    return HttpResponse("OK")


__all__ = [
    "profile",
]
