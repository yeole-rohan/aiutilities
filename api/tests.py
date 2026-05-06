import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from .authentication import APIKeyAuthentication
from .models import APIKey

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", email="alice@example.com", password="pass")


@pytest.fixture
def api_key(user):
    return APIKey.objects.create(user=user, name="test-key")


# ── APIKey model ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAPIKey:
    def test_key_auto_generated(self, api_key):
        assert len(api_key.key) > 20

    def test_keys_are_unique(self, user):
        k1 = APIKey.objects.create(user=user, name="k1")
        k2 = APIKey.objects.create(user=user, name="k2")
        assert k1.key != k2.key

    def test_active_by_default(self, api_key):
        assert api_key.is_active

    def test_str(self, api_key):
        assert "test-key" in str(api_key)


# ── APIKeyAuthentication ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAPIKeyAuthentication:
    def _request(self, header=None):
        factory = APIRequestFactory()
        request = factory.get("/")
        if header:
            request.META["HTTP_AUTHORIZATION"] = header
        return request

    def test_valid_key_authenticates(self, api_key):
        auth = APIKeyAuthentication()
        request = self._request(f"Key {api_key.key}")
        user, key = auth.authenticate(request)
        assert user == api_key.user
        assert key == api_key

    def test_invalid_key_raises(self, db):
        auth = APIKeyAuthentication()
        request = self._request("Key notarealkey")
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    def test_wrong_scheme_returns_none(self, api_key):
        auth = APIKeyAuthentication()
        request = self._request(f"Bearer {api_key.key}")
        assert auth.authenticate(request) is None

    def test_no_header_returns_none(self, db):
        auth = APIKeyAuthentication()
        request = self._request()
        assert auth.authenticate(request) is None

    def test_inactive_key_raises(self, api_key):
        api_key.is_active = False
        api_key.save()
        auth = APIKeyAuthentication()
        request = self._request(f"Key {api_key.key}")
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)
