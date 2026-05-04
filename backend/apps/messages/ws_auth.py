"""Validate JWT access tokens for WebSocket connections (query string)."""

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


def user_from_access_token(raw_token: str | None):
    if not raw_token or not str(raw_token).strip():
        return None
    try:
        auth = JWTAuthentication()
        validated = auth.get_validated_token(str(raw_token).strip())
        return auth.get_user(validated)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return None
