from django.contrib import admin

from .models import Invitation, Organization, OrganizationMember


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization Admin."""

    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """Organization Member Admin."""

    list_display = ("organization", "user", "role")
    list_filter = ("role",)
    search_fields = ("organization__name", "user__username")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Invitation Admin."""

    list_display = ("organization", "email", "role", "email_sent")
    list_filter = ("role", "organization", "email_sent")
    search_fields = ("organization__name", "email")
    list_editable = ("email_sent",)
