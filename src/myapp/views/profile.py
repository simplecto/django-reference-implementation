from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from allauth.socialaccount.models import SocialAccount


@login_required
def profile(request: HttpRequest) -> HttpResponse:
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
