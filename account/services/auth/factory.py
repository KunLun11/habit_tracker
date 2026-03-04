from account.services.auth.token_generator import (
    AccessTokenGenerator,
    RefreshTokenGenerator,
)


class TokenFactory:
    @staticmethod
    def get_access_token() -> AccessTokenGenerator:
        return AccessTokenGenerator()

    @staticmethod
    def get_refresh_token() -> RefreshTokenGenerator:
        return RefreshTokenGenerator()

    @staticmethod
    def get_all_tokens() -> dict:
        return {
            "access": TokenFactory.get_access_token(),
            "refresh": TokenFactory.get_refresh_token(),
        }

    @staticmethod
    def validate_access_token(token: str) -> dict:
        return TokenFactory.get_access_token().validate(token)

    @staticmethod
    def validate_refresh_token(token: str) -> dict:
        return TokenFactory.get_refresh_token().validate(token)
