from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # Auth
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User
    path("me/", views.me, name="me"),
    # Orgs
    path("orgs/", views.orgs_list, name="orgs"),
    # CUSTOMIZE: add your own API endpoints here
]
