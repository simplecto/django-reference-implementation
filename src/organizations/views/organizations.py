from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from organizations.forms import (
    DeleteOrganizationForm,
    OrganizationForm,
)
from organizations.models import Organization, OrganizationMember

if TYPE_CHECKING:
    from django.db.models import QuerySet


class OrganizationListView(LoginRequiredMixin, ListView):
    """List view for organizations."""

    model: type[Organization] = Organization
    template_name = "organizations/index.html"

    def get_queryset(self) -> QuerySet:
        """Get queryset for the view."""
        return self.model.objects.filter(members__user=self.request.user)


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
    org_member = get_object_or_404(OrganizationMember, organization__slug=slug, user=request.user)

    context = {
        "organization": org_member.organization,
        "org_member": org_member,
    }

    return render(request, "organizations/detail.html", context)


@login_required
def invite_logs(request: HttpRequest, slug: str) -> HttpResponse:
    """View invitation logs for an organization.

    Args:
    ----
        request: HttpRequest object.
        slug: Slug of the organization.

    Returns:
    -------
        HttpResponse object.

    """
    org_member = get_object_or_404(OrganizationMember, organization__slug=slug, user=request.user)

    if not org_member.can_admin:
        messages.error(request, "You do not have permission to view invite logs.")
        return HttpResponse(status=403)

    logs = org_member.organization.invitation_logs.all()

    context = {
        "organization": org_member.organization,
        "logs": logs,
    }

    return render(request, "organizations/invite_logs.html", context)


def delete_organization(request: HttpRequest, slug: str) -> HttpResponse:
    """Delete an organization.

    Args:
    ----
        request: HttpRequest object.
        slug: Slug of the organization.

    Returns:
    -------
        HttpResponse object.

    """
    org_member = get_object_or_404(OrganizationMember, organization__slug=slug, user=request.user)

    if not org_member.is_owner:
        messages.error(request, "You do not have permission to delete this organization.")
        return HttpResponse(status=403)

    if request.method == "POST":
        form = DeleteOrganizationForm(request.POST)
        if form.is_valid():
            org_member.organization.delete()
            messages.success(request, "Organization deleted successfully.")
            return redirect("organizations:list")
    else:
        form = DeleteOrganizationForm()

    context = {
        "organization": org_member.organization,
        "form": form,
    }

    return render(request, "organizations/delete_organization.html", context)
