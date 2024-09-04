from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.text import slugify
from organizations.models import Organization, OrganizationMember, Invitation


class OrganizationModelTests(TestCase):
    def test_organization_str_returns_name(self):
        org = Organization.objects.create(name="Test Org")
        self.assertEqual(str(org), "Test Org")

    def test_organization_save_generates_slug(self):
        org = Organization.objects.create(name="Test Org")
        self.assertEqual(org.slug, slugify("Test Org").lower())

    def test_organization_member_str_returns_user_and_org(self):
        user = User.objects.create_user(username="testuser", password="password")
        org = Organization.objects.create(name="Test Org")
        member = OrganizationMember.objects.create(user=user, organization=org)
        self.assertEqual(str(member), f"{user} - {org}")

    def test_organization_member_can_admin_returns_true_for_owner(self):
        user = User.objects.create_user(username="testuser", password="password")
        org = Organization.objects.create(name="Test Org")
        member = OrganizationMember.objects.create(
            user=user, organization=org, role=OrganizationMember.RoleChoices.OWNER
        )
        self.assertTrue(member.can_admin)

    def test_organization_member_can_admin_returns_false_for_member(self):
        user = User.objects.create_user(username="testuser", password="password")
        org = Organization.objects.create(name="Test Org")
        member = OrganizationMember.objects.create(
            user=user, organization=org, role=OrganizationMember.RoleChoices.MEMBER
        )
        self.assertFalse(member.can_admin)

    def test_invitation_str_returns_email(self):
        org = Organization.objects.create(name="Test Org")
        inviter = User.objects.create_user(username="inviter", password="password")
        invitee_email = "invitee@example.com"
        invitation = Invitation.objects.create(
            organization=org, invited_by=inviter, email=invitee_email
        )
        self.assertEqual(str(invitation), invitee_email)

    def test_invitation_save_generates_invite_key(self):
        org = Organization.objects.create(name="Test Org")
        inviter = User.objects.create_user(username="inviter", password="password")
        invitee_email = "invitee@example.com"
        invitation = Invitation.objects.create(
            organization=org, invited_by=inviter, email=invitee_email
        )
        self.assertIsNotNone(invitation.invite_key)

    def test_invitation_save_sets_user_if_email_matches(self):
        org = Organization.objects.create(name="Test Org")
        inviter = User.objects.create_user(username="inviter", password="password")
        invitee = User.objects.create_user(
            username="invitee", email="invitee@example.com", password="password"
        )
        invitation = Invitation.objects.create(
            organization=org, invited_by=inviter, email="invitee@example.com"
        )
        self.assertEqual(invitation.user, invitee)
