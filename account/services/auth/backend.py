from typing import Optional

import jwt


class TokenBackend:
    @staticmethod
    def encode(
        payload: dict[str, any],
        key: str,
        algorithm: str,
        headers: Optional[dict] = None,
    ) -> str:
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dict")

        try:
            token = jwt.encode(
                payload,
                key,
                algorithm=algorithm,
                headers=headers,
            )
            if isinstance(token, bytes):
                token = token.decode("utf-8")
            return token
        except Exception as e:
            return f"Encoding failed: {e}"

    @staticmethod
    def decode(
        token: str,
        key: str,
        algorithms: list[str] = None,
        verify: bool = True,
        **kwargs,
    ) -> dict[str, any]:
        if algorithms is None:
            algorithms = ["HS256"]
        try:
            return jwt.decode(
                token,
                key,
                algorithms=algorithms,
                options={
                    "verify_exp": verify,
                    "verify_signature": verify,
                    "varify_iat": verify,
                    "verify_nbf": verify,
                    "verify_iss": False,
                    "verify_aud": False,
                },
                **kwargs,
            )
        except jwt.ExpiredSignatureError:
            raise "Token has expired"
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {e}")

    @staticmethod
    def verify_signature(token: str, key: str) -> bool:
        try:
            jwt.decode(token, key, options={"verify_exp": False})
            return True
        except jwt.InvalidSignatureError:
            return False
