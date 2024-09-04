from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrganizationForm, OrganizationInviteForm
from .models import Invitation, Organization, OrganizationMember


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


@login_required
def invite(request: HttpRequest, slug: str) -> HttpResponse:
    """Invite a user to an organization.

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

    if not org_member.can_admin:
        messages.error(request, "You do not have permission to invite users.")
        return redirect("organizations:detail", slug=slug)

    if request.method == "POST":
        form = OrganizationInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            role = form.cleaned_data["role"]

            # create the invite record
            Invitation.objects.create(
                organization=org_member.organization,
                invited_by=request.user,
                email=email,
                role=role,
            )

            messages.success(request, f"Invited {email} to the organization.")
            return redirect("organizations:detail", slug=slug)

    else:
        form = OrganizationInviteForm()

    return render(request, "organizations/invite.html", {"form": form})
