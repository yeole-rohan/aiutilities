from django.urls import path

from . import views
from .landing import landing

app_name = "accounts"

urlpatterns = [
    path("", landing, name="landing"),
    path("profile/", views.profile, name="profile"),
]
