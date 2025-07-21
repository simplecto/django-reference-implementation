# tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember, Invitation
from organizations.forms import OrganizationInviteForm, AcceptInviteChangePasswordForm

User = get_user_model()


class OrganizationInviteFormTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="password")
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="password")
        self.member = User.objects.create_user(username="member", email="member@example.com", password="password")

        OrganizationMember.objects.create(
            user=self.owner,
            organization=self.organization,
            role=OrganizationMember.RoleChoices.OWNER,
        )
        OrganizationMember.objects.create(
            user=self.admin,
            organization=self.organization,
            role=OrganizationMember.RoleChoices.ADMIN,
        )
        OrganizationMember.objects.create(
            user=self.member,
            organization=self.organization,
            role=OrganizationMember.RoleChoices.MEMBER,
        )

    def test_form_initialization(self):
        form = OrganizationInviteForm(initial={"organization": self.organization, "invited_by": self.owner})
        self.assertIn("role", form.fields)
        self.assertEqual(len(form.fields["role"].choices), 3)  # OWNER, ADMIN, MEMBER

        form = OrganizationInviteForm(initial={"organization": self.organization, "invited_by": self.admin})
        # Admin users see all 3 choices because form filtering logic is only for non-owners
        # The validation happens in clean_role method instead
        self.assertEqual(len(form.fields["role"].choices), 3)  # OWNER, ADMIN, MEMBER

    def test_clean_role(self):
        form_data: dict = {
            "email": "newuser@example.com",
            "role": OrganizationMember.RoleChoices.OWNER,
        }
        form = OrganizationInviteForm(
            data=form_data,
            initial={"organization": self.organization, "invited_by": self.admin},
        )
        form.instance.organization = self.organization
        form.instance.invited_by = self.admin
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Only owners can assign owner roles.",
            form.errors["role"],
        )

    def test_clean_invited_by_has_permissions(self):
        form_data = {
            "email": "newuser@example.com",
            "role": OrganizationMember.RoleChoices.MEMBER,
        }
        form = OrganizationInviteForm(
            data=form_data,
            initial={"organization": self.organization, "invited_by": self.member},
        )
        form.instance.organization = self.organization
        form.instance.invited_by = self.member
        self.assertFalse(form.is_valid())
        self.assertIn("Only admins can invite users.", form.errors["__all__"])

    def test_clean(self):
        form_data = {
            "email": "member@example.com",
            "role": OrganizationMember.RoleChoices.MEMBER,
        }
        form = OrganizationInviteForm(
            data=form_data,
            initial={"organization": self.organization, "invited_by": self.owner},
        )
        form.instance.organization = self.organization
        form.instance.invited_by = self.owner
        self.assertFalse(form.is_valid())
        self.assertIn("User is already a member of this organization.", form.errors["__all__"])

        form_data = {
            "email": "newuser@example.com",
            "role": OrganizationMember.RoleChoices.MEMBER,
        }
        Invitation.objects.create(organization=self.organization, email="newuser@example.com")
        form = OrganizationInviteForm(
            data=form_data,
            initial={"organization": self.organization, "invited_by": self.owner},
        )
        form.instance.organization = self.organization
        form.instance.invited_by = self.owner
        self.assertFalse(form.is_valid())
        self.assertIn("User is already invited to this organization.", form.errors["__all__"])


class AcceptInviteChangePasswordFormTest(TestCase):
    def test_form_valid(self):
        form_data = {
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!",
        }
        form = AcceptInviteChangePasswordForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_passwords_do_not_match(self):
        form_data = {
            "password": "ValidPassword123!",
            "confirm_password": "DifferentPassword123!",
        }
        form = AcceptInviteChangePasswordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Passwords do not match.", form.errors["__all__"])

    def test_form_invalid_password_blank(self):
        form_data = {"password": "", "confirm_password": ""}
        form = AcceptInviteChangePasswordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Password is required.", form.errors["__all__"])

    def test_form_invalid_password_fails_validation(self):
        form_data = {"password": "short", "confirm_password": "short"}
        form = AcceptInviteChangePasswordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "This password is too short. It must contain at least 8 characters.",
            form.errors["__all__"],
        )
