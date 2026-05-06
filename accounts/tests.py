import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass"
        )
        assert user.pk is not None
        assert user.email == "alice@example.com"
        assert user.is_active

    def test_str(self):
        user = User.objects.create_user(username="bob", email="bob@example.com", password="pass")
        assert "bob" in str(user)

    def test_avatar_url_blank_by_default(self):
        user = User.objects.create_user(
            username="carol", email="carol@example.com", password="pass"
        )
        assert user.avatar_url == ""
