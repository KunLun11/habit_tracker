from django.core.exceptions import ValidationError
from django.db import transaction

from account.models.users import CustomUser
from account.services.account.verification import VerificationService
from account.services.auth.factory import TokenFactory


class RegistrationService:
    @staticmethod
    def register_user(email: str, password: str, **extra_fields) -> CustomUser:
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("User with email already exists")

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_active=False,
                email_activated=False,
                phone_activated=False,
                **extra_fields,
            )
        confirmation_code = VerificationService.create_verification_code(user)
        VerificationService.send_verification_email(email, confirmation_code.code)
        return user

    @staticmethod
    def verify_user_email(email: str, confirmation_code: str) -> CustomUser:
        try:
            user = CustomUser.objects.get(email=email, is_active=False)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found or already active")

        verification_code = VerificationService.verify_code(email, confirmation_code)
        verification_code.is_used = True
        verification_code.save()

        user.email_activated = True
        user.is_active = True
        user.save()

        access_token = TokenFactory().get_access_token().generate(user)
        refresh_token = TokenFactory().get_refresh_token().generate(user)

        return {
            "email": user.email,
            "access": access_token,
            "refresh": refresh_token,
        }

    @staticmethod
    def login_user(email: str, password: str) -> dict:
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
        if not user.check_password(password):
            return None
        access_token = TokenFactory().get_access_token().generate(user)
        refresh_token = TokenFactory().get_refresh_token().generate(user)

        return {
            "access": access_token,
            "refresh": refresh_token,
        }

    @staticmethod
    def resend_confirmation_code(email: str) -> None:
        try:
            user = CustomUser.objects.get(email=email, is_active=False)
        except CustomUser.DoesNotExist:
            return ValidationError("User not found")
        if user.email_activated:
            raise ValidationError("Email already active")
        confirmation_code = VerificationService.create_verification_code(user)
        VerificationService.send_verification_email(email, confirmation_code.code)
