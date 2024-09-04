import uuid

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from organizations.forms import (
    AcceptInviteChangePasswordForm,
    OrganizationInviteForm,
)
from organizations.models import Invitation, OrganizationMember


@login_required
@require_http_methods(["POST"])
def remove_member(request: HttpRequest, slug: str) -> HttpResponse:
    """Remove a member from an organization.

    Args:
    ----
        request: HttpRequest object.
        slug: Slug of the organization.

    Returns:
    -------
        HttpResponse object.

    """
    user_id = request.POST.get("user_id")
    target = get_object_or_404(OrganizationMember, user_id=user_id)

    # requesting user must be a member of the organization, otherwise 404
    org_member = get_object_or_404(
        OrganizationMember, organization__slug=slug, user=request.user
    )

    org = org_member.organization

    # an organization owner can only remove themselves if there are other owners
    if (
        org_member.role == OrganizationMember.RoleChoices.OWNER
        and org.owners.count() == 1
    ):
        messages.error(request, "You cannot remove yourself as the only owner.")
        return redirect("organizations:detail", slug=slug)

    # you can remove yourself from the organization
    if target == org_member:
        target.delete()
        messages.success(request, "You have left the organization.")
        return redirect("profile")

    # only owners and admins can remove members
    if not org_member.can_admin:
        messages.error(request, "You do not have permission to remove members.")
        return redirect("organizations:detail", slug=slug)

    # we made it this far, so the user can be removed
    target.delete()
    messages.success(request, "User removed from the organization.")

    return redirect("organizations:detail", slug=slug)


@login_required
def invite_user(request: HttpRequest, slug: str) -> HttpResponse:
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
        return HttpResponse(status=403)

    if request.method == "POST":
        form = OrganizationInviteForm(request.POST)
        form.instance.organization = org_member.organization
        form.instance.invited_by = request.user

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
        initial = {"organization": org_member.organization, "invited_by": request.user}
        form = OrganizationInviteForm(initial=initial)

    return render(request, "organizations/invite.html", {"form": form})


def accept_invite(request: HttpRequest, token: str) -> HttpResponse:
    """Accept an organization invite.

    Args:
    ----
        request: HttpRequest object.
        token: Token of the invite.

    Returns:
    -------
        HttpResponse object.

    """
    user = request.user

    invite = get_object_or_404(Invitation, invite_key=token)

    if invite.accepted_at:
        messages.error(request, "This invite is no longer valid.")
        return HttpResponse(status=403)

    # the user and the invited user must match
    if user != invite.user and user.is_authenticated:
        messages.error(request, "You are not authorized to accept this invite.")

    if user.is_authenticated and user == invite.user:
        # accept the invite
        OrganizationMember.objects.create(
            organization=invite.organization,
            user=user,
            role=invite.role,
        )
        invite.accepted_at = timezone.now()
        invite.save()

        messages.success(request, "You have joined the organization.")
        return redirect("organizations:detail", slug=invite.organization.slug)

    # if the invited user does not have an account, create one
    if user.is_anonymous and not invite.user_exists:
        # create a new user
        user = User.objects.create_user(
            email=invite.email,
            username=invite.email,
            password=uuid.uuid4().hex,
        )

        # accept the invite
        OrganizationMember.objects.create(
            organization=invite.organization,
            user=user,
            role=invite.role,
        )
        invite.accepted_at = timezone.now()
        invite.save()

        # log the user in
        backend = "django.contrib.auth.backends.ModelBackend"

        login(request, user, backend=backend)

        messages.success(
            request, "You have joined the organization. Please set your password."
        )
        return redirect(
            "organizations:accept_invite_change_password", token=invite.invite_key
        )

    messages.error(request, "You are not authorized to accept this invite.")

    return render(request, "organizations/accept_invite.html", {"invite": invite})


def decline_invite(request: HttpRequest, token: str) -> HttpResponse:
    """Decline an organization invite.

    Args:
    ----
        request: HttpRequest object.
        token: Token of the invite.

    Returns:
    -------
        HttpResponse object.

    """
    user = request.user

    invite = get_object_or_404(Invitation, invite_key=token)

    if invite.accepted_at:
        messages.error(request, "This invite is no longer valid.")
        return HttpResponse(status=403)

    # the user and the invited user must match
    if user != invite.user and user.is_authenticated:
        messages.error(request, "You are not authorized to accept this invite.")

    return HttpResponse(status=200)


def accept_invite_change_password(request: HttpRequest, token: str) -> HttpResponse:
    """Change password after accepting an invite.

    Args:
    ----
        request: HttpRequest object.
        token: Token of the invite.

    Returns:
    -------
        HttpResponse object.

    """
    user = request.user
    get_object_or_404(Invitation, invite_key=token)

    if request.method == "POST":
        form = AcceptInviteChangePasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(request, "Password set successfully.")
            return redirect("organizations:index")
    else:
        form = AcceptInviteChangePasswordForm()

    return render(
        request, "organizations/accept_invite_change_password.html", {"form": form}
    )