from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from organizations.forms import (
    OrganizationForm,
)
from organizations.models import Organization, OrganizationMember


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Home view.

    Args:
    ----
        request: HttpRequest object.

    Returns:
    -------
        HttpResponse object.

    """
    organizations = Organization.objects.filter(members__user=request.user)

    org_form = OrganizationForm()

    context = {
        "organizations": organizations,
        "org_form": org_form,
    }

    return render(request, "organizations/index.html", context)


@login_required
def create_organization(request: HttpRequest) -> HttpResponse:
    """Create an organization view.

    Args:
    ----
        request: HttpRequest object.

    Returns:
    -------
        HttpResponse object.

    """
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save()
            OrganizationMember.objects.create(
                organization=org,
                user=request.user,
                role=OrganizationMember.RoleChoices.OWNER,
            )
            messages.success(request, "Organization created successfully.")
            return redirect("organizations:detail", slug=org.slug)
    else:
        form = OrganizationForm()

    return render(request, "organizations/create.html", {"form": form})


@login_required
def detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Organization detail view.

    Args:
    ----
        request: HttpRequest object.
        slug: Slug of the organization.

    Returns:
    -------
        HttpResponse object.

    """
    org_member = get_object_or_404(
        OrganizationMember, organization__slug=slug, user=request.user
    )

    context = {
        "organization": org_member.organization,
        "org_member": org_member,
    }

    return render(request, "organizations/detail.html", context)