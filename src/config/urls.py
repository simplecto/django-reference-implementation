from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),
    path('health-check', views.health_check, name='health-check'),
]
