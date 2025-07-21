"""Tests for organizations app."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from myapp.models import SiteConfiguration
from organizations.models import Organization, OrganizationMember


class OrganizationViewsTests(TestCase):
    """Organization views tests."""

    def setUp(self):
        # Create SiteConfiguration singleton for tests
        SiteConfiguration.objects.get_or_create()

        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.organization = Organization.objects.create(name="Test Org", slug="test-org")
        self.org_member = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role=OrganizationMember.RoleChoices.OWNER,
        )

    def test_index_view_renders_correct_template(self):
        response = self.client.get(reverse("organizations:list"))
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
        response = self.client.get(reverse("organizations:detail", args=[self.organization.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/detail.html")
