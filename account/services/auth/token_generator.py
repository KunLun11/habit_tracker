from datetime import datetime, timedelta, timezone
from uuid import uuid4

from django.conf import settings

from account.services.auth.backend import TokenBackend
from account.services.auth.exceptions import InvalidTokenError


class TokenGenerator:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        lifetime: timedelta,
    ):
        self.secret_key: str = secret_key
        self.algorithm: str = algorithm
        self.lifetime: timedelta = lifetime

    def _get_jti(self) -> str:
        return uuid4().hex

    def _create_base_payload(self, user, token_type):
        iat = datetime.now(tz=timezone.utc)
        exp = iat + self.lifetime

        return {
            "token_type": token_type,
            "user_id": str(user.id),
            "email": user.email,
            "jti": self._get_jti(),
            "iat": int(iat.timestamp()),
            "exp": int(exp.timestamp()),
        }


class AccessTokenGenerator(TokenGenerator):
    def __init__(self):
        super().__init__(
            secret_key=settings.JWT_SIGNING_KEY,
            algorithm=settings.JWT_ALGORITHM,
            lifetime=settings.JWT_ACCESS_TOKEN_LIFETIME,
        )

    def generate(self, user) -> str:
        payload = self._create_base_payload(user, token_type="access")
        return TokenBackend.encode(payload, self.secret_key, self.algorithm)

    def validate(self, token: str) -> dict:
        payload = TokenBackend.decode(token, self.secret_key, self.algorithm)
        if payload.get("token_type") != "access":
            raise InvalidTokenError("Not a access token")
        return payload


class RefreshTokenGenerator(TokenGenerator):
    def __init__(self):
        super().__init__(
            secret_key=settings.JWT_SIGNING_KEY,
            algorithm=settings.JWT_ALGORITHM,
            lifetime=settings.JWT_REFRESH_TOKEN_LIFETIME,
        )

    def generate(self, user) -> str:
        payload = self._create_base_payload(user, token_type="refresh")
        return TokenBackend.encode(payload, self.secret_key, self.algorithm)

    def validate(self, token: str) -> dict:
        payload = TokenBackend.decode(token, self.secret_key, self.algorithm)
        if payload.get("token_type") != "refresh":
            raise InvalidTokenError("Not a refresh token")
        return payload
