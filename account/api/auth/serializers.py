from rest_framework import serializers

from account.services.auth.authentication import AuthService


class TokenObtainPairSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )
    email = serializers.EmailField(required=True, write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def validate(self, attrs: dict) -> dict:
        email = attrs["email"]
        password = attrs["password"]
        auth_service = AuthService()
        user = auth_service.auth_user(email, password)
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        auth_service = AuthService()
        return auth_service.create_tokens_for_user(validated_data["user"])


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)

    def validate(self, attrs: dict) -> dict:
        refresh_token = attrs["refresh"]
        auth_service = AuthService()
        user, new_access_token = auth_service.refresh_access_token(refresh_token)
        attrs["user"] = user
        attrs["access"] = new_access_token
        return attrs

    def create(self, validated_data):
        return {"access": validated_data["access"]}


class TokenVerifySerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    ok = serializers.BooleanField(read_only=True)
    user_id = serializers.CharField(read_only=True)

    def validate(self, attrs: dict) -> dict:
        refresh_token = attrs["refresh"]
        auth_service = AuthService()
        user, is_valid = auth_service.validate_refresh_token(refresh_token)
        attrs["ok"] = is_valid
        if user and is_valid:
            attrs["user_id"] = str(user.id)
        return attrs

    def create(self, validated_data):
        result = {"ok": validated_data["ok"]}
        if validated_data["user_id"]:
            result["user_id"] = validated_data["user_id"]
        return result
