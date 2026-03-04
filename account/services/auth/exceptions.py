class TokenError(Exception):
    pass


class TokenExpiredError(TokenError):
    pass


class InvalidTokenError(TokenError):
    pass


class UserNotFoundError(TokenError):
    pass
