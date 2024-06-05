from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount


def index(request):
    return render(request, "home.html")


def health_check(request):
    return HttpResponse("OK")


def send_email(request):
    return render(request, "email.html")


def send_sms(request):
    return render(request, "sms.html")


@login_required
def profile(request):
    social_accounts = SocialAccount.objects.all()

    return render(
        request,
        "account/profile.html",
        {
            # 'providers': providers,
            "social_accounts": social_accounts,
        },
    )
