from django.urls import path

from . import views
from .landing import landing

app_name = "accounts"

urlpatterns = [
    path("", landing, name="landing"),
    path("profile/", views.profile, name="profile"),
    path(
        "192896c3ad0a4d6e8f7696a94c0a23ea.txt",
        views.IndexNowTxtView.as_view(),
        name="indexnow",
    ),
]
