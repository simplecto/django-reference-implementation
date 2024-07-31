from django.contrib.sites.models import Site


def site_name(request):
    current_site = Site.objects.get_current()
    return {"site_name": current_site.name}
