"""Tests for invitation views."""

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import uuid

from myapp.models import SiteConfiguration
from organizations.models import Organization, OrganizationMember, Invitation


class InvitationViewsTests(TestCase):
    """Invitation views tests."""

    def setUp(self):
        # Create SiteConfiguration singleton for tests
        SiteConfiguration.objects.get_or_create()

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


class AcceptInviteChangePasswordTests(TestCase):
    def setUp(self):
        # Create SiteConfiguration singleton for tests
        SiteConfiguration.objects.get_or_create()

        self.user = User.objects.create_user(
            username="testuser", password="old_password"
        )
        self.organization = Organization.objects.create(
            name="Test Org", slug="test-org"
        )
        self.invitation = Invitation.objects.create(
            email="testuser@example.com",
            organization=self.organization,
            invited_by=self.user,
            accepted_at=timezone.now(),
        )
        self.client.login(username="testuser", password="old_password")
        self.url = reverse("organizations:accept_invite_change_password")

    def test_accept_invite_change_password_success(self):
        response = self.client.post(
            self.url, {"password": "new_password", "confirm_password": "new_password"}
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.check_password("new_password"))

    def test_accept_invite_change_password_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "organizations/accept_invite_change_password.html"
        )

    def test_accept_invite_change_password_invalid_form(self):
        response = self.client.post(
            self.url, {"password": "123", "confirm_password": "123"}
        )
        self.assertEqual(response.status_code, 400)


class DeclineInviteTests(TestCase):
    def setUp(self):
        # Create SiteConfiguration singleton for tests
        SiteConfiguration.objects.get_or_create()

        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.organization = Organization.objects.create(name="Test Organization")
        self.invitation = Invitation.objects.create(
            organization=self.organization,
            invited_by=self.user,
            email="invitee@example.com",
        )
        self.invite_key = self.invitation.invite_key
        self.url = reverse(
            "organizations:decline_invite", args=[self.invitation.invite_key]
        )

    def test_decline_invite_post(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/decline_invite_success.html")
        self.assertFalse(Invitation.objects.filter(invite_key=self.invite_key).exists())

    def test_decline_invite_get(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/decline_invite.html")
        self.assertTrue(Invitation.objects.filter(invite_key=self.invite_key).exists())

    def test_decline_invite_invalid_token(self):
        self.client.login(username="testuser", password="12345")
        invalid_token = uuid.uuid4()
        invalid_url = reverse("organizations:decline_invite", args=[invalid_token])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)


class AcceptInviteTests(TestCase):
    def setUp(self):
        # Create SiteConfiguration singleton for tests
        SiteConfiguration.objects.get_or_create()

        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.organization = Organization.objects.create(
            name="Test Org", slug="test-org"
        )

        self.inviting_user = User.objects.create_user(
            username="inviter", password="12345"
        )
        self.invite = Invitation.objects.create(
            organization=self.organization,
            invited_by=self.inviting_user,
            user=self.user,
            email="invitee@example.com",
            role=OrganizationMember.RoleChoices.MEMBER,
        )

        self.invite_no_user = Invitation.objects.create(
            organization=self.organization,
            invited_by=self.inviting_user,
            user=None,
            email="invitee_anon@example.com",
            role=OrganizationMember.RoleChoices.MEMBER,
        )

        self.url = reverse("organizations:accept_invite", args=[self.invite.invite_key])

        self.anon_url = reverse(
            "organizations:accept_invite", args=[self.invite_no_user.invite_key]
        )

    def test_accept_invite_wrong_invite_key(self):
        response = self.client.get(
            reverse("organizations:accept_invite", args=[uuid.uuid4()])
        )
        self.assertEqual(response.status_code, 404)

    def test_accept_invite_unauthorized_user(self):
        other_user = User.objects.create_user(username="otheruser", password="12345")
        self.client.login(username="otheruser", password="12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_accept_invite_authenticated_user(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            OrganizationMember.objects.filter(
                user=self.user, organization=self.organization
            ).exists()
        )

    def test_accept_invite_anonymous_user_account_not_exists(self):
        response = self.client.get(self.anon_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("organizations:accept_invite_change_password"),
        )

    def test_accept_invite_anonymous_user_account_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account_login"))
