"""Forms for the organizations app."""

from django import forms

from organizations.models import Organization, OrganizationMember


class OrganizationForm(forms.ModelForm):
    """Form for the organization model."""

    class Meta:
        """Meta options for the organization form."""

        model = Organization
        fields = ["name", "description"]  # noqa: RUF012


class OrganizationInviteForm(forms.Form):
    """Form to invite users."""

    role = forms.ChoiceField(
        choices=OrganizationMember.RoleChoices.choices,
        initial=OrganizationMember.RoleChoices.MEMBER,
    )
    email = forms.EmailField()

    # remove OWNER choice from choice field
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [
            (choice, label)
            for choice, label in OrganizationMember.RoleChoices.choices
            if choice != OrganizationMember.RoleChoices.OWNER
        ]
