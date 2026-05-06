from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Key "):
            return None
        raw_key = auth[4:].strip()
        try:
            key = APIKey.objects.select_related("user").get(key=raw_key, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key.")
        return (key.user, key)

    def authenticate_header(self, request):
        return 'Key realm="api"'
