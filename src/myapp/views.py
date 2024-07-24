"""All of our Django views will be defined in this file."""

import django.http
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount


def index(request: django.http.HttpRequest) -> django.http.HttpResponse:
    """
    Home page view. This is the first page that the user sees when they visit
    the site
    :param request:
    :return:
    """
    return render(request, "home.html")


def health_check(request) -> django.http.HttpResponse:
    """
    Health check view. Used by the load balancer or Docker to check if the
    server is up
    :return:
    """
    return django.http.HttpResponse("OK")


@login_required
def profile(request: django.http.HttpRequest) -> django.http.HttpResponse:
    """
    Profile page view. This page shows the user's profile information
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
