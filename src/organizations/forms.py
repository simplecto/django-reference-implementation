"""Forms for the organizations app."""

from django import forms
from django.contrib.auth.password_validation import validate_password

from organizations.models import Invitation, Organization, OrganizationMember


class OrganizationForm(forms.ModelForm):
    """Form for the organization model."""

    class Meta:
        """Meta options for the organization form."""

        model = Organization
        fields = ["name", "description"]  # noqa: RUF012


class OrganizationInviteForm(forms.ModelForm):
    """Form to invite users."""

    class Meta:
        """Meta options for the organization invite form."""

        model = Invitation
        fields = ["email", "role"]  # noqa: RUF012

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize the form."""
        super().__init__(*args, **kwargs)

        if "initial" in kwargs:
            organization = kwargs.get("initial").get("organization")
            user = kwargs.get("initial").get("invited_by")

            if not organization.is_owner(user):
                self.fields["role"].choices = [
                    (OrganizationMember.RoleChoices.ADMIN, "Admin"),
                    (OrganizationMember.RoleChoices.MEMBER, "Member"),
                ]

    def clean_role(self) -> str:
        """Validate that only an owner can assign an owner role."""
        role = self.cleaned_data["role"]
        organization = self.instance.organization
        user = self.instance.invited_by

        if role == OrganizationMember.RoleChoices.OWNER and not organization.is_owner(
            user
        ):
            msg = "Only owners can assign owner roles."
            raise forms.ValidationError(msg)

        return role

    # validate that the requesting user is an owner of the organization and that the email is not already a member
    def clean(self) -> None:
        """Validate that the requesting user is an owner of the organization."""
        cleaned_data = super().clean()
        organization = self.instance.organization
        user = self.instance.invited_by
        email = cleaned_data.get("email")

        if not organization.has_admin_permission(user):
            msg = "Only admins can invite users."
            raise forms.ValidationError(msg)

        if organization.members.filter(user__email=email).exists():
            msg = "User is already a member of this organization."
            raise forms.ValidationError(msg)

        # test that this invitee is not already invited
        if Invitation.objects.filter(organization=organization, email=email).exists():
            msg = "User is already invited to this organization."
            raise forms.ValidationError(msg)

        return cleaned_data


# form to change password after invite
class AcceptInviteChangePasswordForm(forms.Form):
    """Form to change password after accepting an invite."""

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self) -> None:
        """Validate that the passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            msg = "Passwords do not match."
            raise forms.ValidationError(msg)

        # blank is the same as null and not allowed
        if not password:
            msg = "Password is required."
            raise forms.ValidationError(msg)

        # Validate password using Django's built-in validators
        try:
            validate_password(password)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages) from e

        return cleaned_data


class DeleteOrganizationForm(forms.Form):
    """Form to delete an organization."""

    confirm = forms.CharField()

    def clean_confirm(self) -> str:
        """Validate that the user has confirmed the deletion."""
        confirm = self.cleaned_data["confirm"]

        if confirm != "DELETE":
            msg = "You must type 'DELETE' to confirm deletion."
            raise forms.ValidationError(msg)

        return confirm
