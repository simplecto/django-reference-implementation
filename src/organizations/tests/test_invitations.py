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

    def test_invite_view_redirects_if_no_permission(self):
        other_user = User.objects.create_user(username="otheruser", password="password")
        self.client.login(username="otheruser", password="password")
        response = self.client.get(
            reverse("organizations:invite", args=[self.organization.slug])
        )
        self.assertEqual(response.status_code, 404)
