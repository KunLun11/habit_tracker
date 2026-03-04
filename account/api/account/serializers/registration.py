from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers

from account.services.account.registration import RegistrationService


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs["password"]
        password_confirm = attrs.pop("password_confirm")
        if password != password_confirm:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_password(seld, value: str):
        try:
            validate_password(value, None)
            return value
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        try:
            RegistrationService.register_user(**validated_data)
            return {
                "email": validated_data["email"],
                "first_name": validated_data.get("first_name", ""),
                "last_name": validated_data.get("last_name", ""),
                "phone": validated_data.get("phone", ""),
                "message": "Регистрация успешна. Подтвердите email.",
            }
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(str(e))


class VerfyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    confirmation_code = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data["confirmation_code"].isdigit():
            raise serializers.ValidationError("Code must contain only digits")
        return data

    def create(self, validated_data):
        try:
            return RegistrationService.verify_user_email(**validated_data)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        return instance


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        try:
            RegistrationService.resend_confirmation_code(**validated_data)
            return {
                "email": validated_data["email"],
                "message": "Code has been resent",
            }
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(str(e))


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        try:
            result = RegistrationService.login_user(**validated_data)
            return {
                "email": validated_data["email"],
                "access_token": result["access"],
                "refresh_token": result["refresh"],
            }
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        return instance


__all__ = [
    "RegistrationSerializer",
    "VerfyEmailSerializer",
    "ResendCodeSerializer",
    "LoginSerializer",
]
