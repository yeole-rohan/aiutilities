from django.urls import path

from . import views

app_name = "orgs"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_org, name="create"),
    path("switch/", views.switch_org, name="switch"),
    path("members/", views.members, name="members"),
    path("members/invite/", views.invite_member, name="invite"),
    path("invite/<uuid:token>/", views.accept_invite, name="accept_invite"),
]
