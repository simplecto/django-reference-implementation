from django.contrib.sites.models import Site
from django.http import HttpRequest


def site_name(request: HttpRequest) -> dict:  # noqa: ARG001
    """Add the site name to the context."""
    current_site = Site.objects.get_current()
    return {"site_name": current_site.name}
