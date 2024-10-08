"""URL configuration for organizations app."""

from django.urls import path

from organizations.views import members, organizations

app_name = "organizations"

urlpatterns = [
    path("create/", organizations.create_organization, name="create_organization"),
    path("<slug:slug>/", organizations.detail, name="detail"),
    path("<slug:slug>/invite/", members.invite_user, name="invite"),
    path("<slug:slug>/remove-member/", members.remove_member, name="remove_member"),
    path("<slug:slug>/invite-logs/", organizations.invite_logs, name="invite_logs"),
    path(
        "<slug:slug>/delete/",
        organizations.delete_organization,
        name="delete_organization",
    ),
    path("accept-invite/<uuid:token>/", members.accept_invite, name="accept_invite"),
    path(
        "accept-invite/change-password/",
        members.accept_invite_change_password,
        name="accept_invite_change_password",
    ),
    path("decline-invite/<uuid:token>/", members.decline_invite, name="decline_invite"),
    path("", organizations.OrganizationListView.as_view(), name="list"),
]
