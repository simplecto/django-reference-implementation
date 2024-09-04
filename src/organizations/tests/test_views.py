"""Tests for organizations app."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from organizations.models import Organization, OrganizationMember


class OrganizationViewsTests(TestCase):
    """Organization views tests."""

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

    def test_home_view_renders_correct_template(self):
        response = self.client.get(reverse("organizations:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/index.html")

    def test_get_create_organization_view_with_permission(self):
        response = self.client.get(reverse("organizations:create_organization"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/create.html")

    def test_create_organization_creates_new_org(self):
        response = self.client.post(
            reverse("organizations:create_organization"),
            {"name": "New Org", "slug": "new-org"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Organization.objects.filter(name="New Org").exists())

    def test_detail_view_renders_correct_template(self):
        response = self.client.get(
            reverse("organizations:detail", args=[self.organization.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/detail.html")

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
