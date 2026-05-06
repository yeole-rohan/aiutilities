from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model. Swap in early — cheaper than migrating later.
    Uses email as the primary identifier via django-allauth.
    """

    # CUSTOMIZE: add extra profile fields here
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True, max_length=300)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.email or self.username
