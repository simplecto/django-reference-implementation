"""Tests for invitation views."""

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from organizations.models import Organization, OrganizationMember


class InvitationViewsTests(TestCase):
    """Invitation views tests."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.organization = Organization.objects.create(
            name="Test Org", slug="test-org"
        )
        self.org_member = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role=OrganizationMember.RoleChoices.OWNER,
        )

        self.user_owner_2 = User.objects.create_user(
            username="owner2", password="password"
        )
        self.org_member_owner_2 = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user_owner_2,
            role=OrganizationMember.RoleChoices.OWNER,
        )

        self.user_member = User.objects.create_user(
            username="testmember", password="password"
        )
        self.org_member_member = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user_member,
            role=OrganizationMember.RoleChoices.MEMBER,
        )

    def test_invite_view_renders_correct_template(self):
        response = self.client.get(
            reverse("organizations:invite", args=[self.organization.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/invite.html")

    def test_invite_view_redirects_if_no_read_permission(self):
        other_user = User.objects.create_user(username="otheruser", password="password")
        self.client.login(username="otheruser", password="password")
        response = self.client.get(
            reverse("organizations:invite", args=[self.organization.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_invite_view_org_member_cannot_invite(self):
        org_member = OrganizationMember.objects.create(
            organization=self.organization,
            user=User.objects.create_user(username="orgmember", password="password"),
            role=OrganizationMember.RoleChoices.MEMBER,
        )
        self.client.login(username="orgmember", password="password")
        response = self.client.get(
            reverse("organizations:invite", args=[self.organization.slug])
        )
        self.assertEqual(response.status_code, 403)

    def test_invite_view_submit_with_invalid_email(self):
        response = self.client.post(
            reverse("organizations:invite", args=[self.organization.slug]),
            {"email": "invalid-email"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "Enter a valid email address."
        )

    def test_invite_view_submit_with_invalid_role(self):
        response = self.client.post(
            reverse("organizations:invite", args=[self.organization.slug]),
            {"email": "test@example.com", "role": "invalid-role"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "role",
            "Select a valid choice. invalid-role is not one of the available choices.",
        )

    def test_invite_view_successful_invite(self):
        response = self.client.post(
            reverse("organizations:invite", args=[self.organization.slug]),
            {
                "email": "test@example.com",
                "role": OrganizationMember.RoleChoices.MEMBER,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.organization.invitations.filter(email="test@example.com").exists()
        )

    def test_remove_member_successfully(self):
        self.client.login(username="owner2", password="password")
        response = self.client.post(
            reverse("organizations:remove_member", args=["test-org"]),
            {"user_id": self.user_member.id},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "User removed from the organization.")
        self.assertRedirects(
            response, reverse("organizations:detail", args=["test-org"])
        )
        self.assertFalse(
            OrganizationMember.objects.filter(user=self.user_member).exists()
        )

    def test_remove_member_no_permission(self):
        other_user = User.objects.create_user(username="otheruser", password="12345")
        other_member = OrganizationMember.objects.create(
            organization=self.organization,
            user=other_user,
            role=OrganizationMember.RoleChoices.MEMBER,
        )
        self.client.login(username="otheruser", password="12345")
        response = self.client.post(
            reverse("organizations:remove_member", args=["test-org"]),
            {"user_id": self.user.id},
        )
        self.assertRedirects(
            response, reverse("organizations:detail", args=["test-org"])
        )
        self.assertTrue(OrganizationMember.objects.filter(user=self.user).exists())

    def test_remove_member_owner_cannot_delete_self(self):
        self.client.login(username="testuser", password="password")
        self.org_member_owner_2.delete()
        response = self.client.post(
            reverse("organizations:remove_member", args=["test-org"]),
            {"user_id": self.user.id},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "You cannot remove yourself as the only owner."
        )
        self.assertRedirects(
            response, reverse("organizations:detail", args=["test-org"])
        )
        self.assertTrue(OrganizationMember.objects.filter(user=self.user).exists())
