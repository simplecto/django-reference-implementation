from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from myapp import views
from django.views.generic import TemplateView


urlpatterns = [
    path('robots.txt',
         TemplateView.as_view(template_name="robots.txt", content_type='text/plain'),
         name="robots-txt"),
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),
    path('health-check', views.health_check, name='health-check'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
