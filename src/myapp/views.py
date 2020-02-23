from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'home.html')


def health_check(request):
    return HttpResponse('OK')


def send_email(request):
    return render(request, "email.html")


def send_sms(request):
    return render(request, "sms.html")


def send_sms(request):
    return render(request, "sms.html")
