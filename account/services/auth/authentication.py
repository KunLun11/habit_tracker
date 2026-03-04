from django.forms import ValidationError
from rest_framework import authentication, exceptions

from account.models.users import CustomUser
from account.services.auth.exceptions import (
    InvalidTokenError,
    TokenError,
    TokenExpiredError,
    UserNotFoundError,
)
from account.services.auth.factory import TokenFactory


class CustomUserAuthentication(authentication.BaseAuthentication):
    header_type = "Bearer"
    header_encoding = "iso-8859-1"
    media_type = "application/json"
    header_name = "HTTP_AUTHORIZATION"
    cookie_name = "access_token"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.header_type_bytes = self.header_type.encode(self.header_encoding)

    def authenticate(self, request):
        auth_header = request.META.get(self.header_name)
        if auth_header:
            return self._authenticate_by_header(auth_header)
        auth_cookie = request.COOKIES.get(self.cookie_name)
        if auth_cookie:
            return self._authenticate_by_token(auth_cookie)
        return None

    def _authenticate_by_header(self, auth_header):
        parts = auth_header.split()
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                "Bad format for header. You need use: Bearer <token>"
            )

        scheme, token = parts
        if scheme.lower() != self.header_type.lower():
            raise exceptions.AuthenticationFailed(
                f"Bad schema auth. Wait the {self.header_type}"
            )
        return self._authenticate_by_token(token)

    def _authenticate_by_token(self, token):
        try:
            payload = TokenFactory.validate_access_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                raise exceptions.AuthenticationFailed(
                    "Invalid token: not found user_id"
                )
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                raise exceptions.AuthenticationFailed("User not found")

            if not user.is_active:
                raise exceptions.AuthenticationFailed("User is not active")
            return user, token
        except TokenExpiredError:
            raise exceptions.AuthenticationFailed("The token has expired")
        except InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")
        except TokenError as e:
            raise exceptions.AuthenticationFailed(f"Token error: {str(e)}")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Authentication error: {str(e)}")

    def authenticate_header(self, request):
        return f'{self.header_type} realm="api"'


class AuthService:
    @staticmethod
    def auth_user(email: str, password: str) -> CustomUser:
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("User with email not found")

        if not user.check_password(password):
            raise ValidationError("Invalid password")
        if not user.is_active:
            raise ValidationError("User not active")
        return user

    @staticmethod
    def create_tokens_for_user(user: CustomUser) -> dict[str, str]:
        access_token = TokenFactory().get_access_token().generate(user)
        refresh_token = TokenFactory().get_refresh_token().generate(user)

        return {
            "access": access_token,
            "refresh": refresh_token,
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> tuple[CustomUser, str]:
        try:
            payload = TokenFactory().validate_refresh_token(refresh_token)
            user_id = payload.get("user_id")
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                raise UserNotFoundError("User not found")
            if not user.is_active:
                raise ValidationError("User not active")
            new_access_tokens = TokenFactory().get_access_token().generate(user)
            return user, new_access_tokens

        except TokenExpiredError:
            raise TokenExpiredError("Refresh token has expired")
        except InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid refresh token: {str(e)}")

    @staticmethod
    def get_user_from_token(token: str, token_type: str = "access") -> CustomUser:
        if token_type == "access":
            payload = TokenFactory.validate_access_token(token)
        elif token_type == "refresh":
            payload = TokenFactory.validate_refresh_token(token)
        else:
            raise InvalidTokenError("Invalid type token")

        user_id = payload.get("user_id")
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise UserNotFoundError("User not found")

    @staticmethod
    def validate_token_pair(access_token: str, refresh_token: str) -> bool:
        try:
            access_payload = TokenFactory.validate_access_token(access_token)
            refresh_payload = TokenFactory.validate_refresh_token(refresh_token)
            if access_payload.get("user_id") != refresh_payload.get("user_id"):
                return False
            return True
        except TokenError:
            return False

    @staticmethod
    def validate_refresh_token(refresh_token: str) -> tuple[CustomUser, bool]:
        try:
            payload = TokenFactory.validate_refresh_token(refresh_token)
            user_id = payload.get("user_id")
            if not user_id:
                return None, False
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return None, False
            if not user.is_active:
                return None, False
            return user, True
        except TokenError:
            return None, False
