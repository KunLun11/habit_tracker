from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from account.models.codes import EmailConfirmationCode
from account.models.users import CustomUser
from config.utils.code_generators import email_confirmation_code_generate


class VerificationService:
    @staticmethod
    def send_verification_email(email: str, code: str) -> None:
        subject = "Подтверждение регистрации"
        message = f"Ваш код подтверждения {code}\nКод действителен в течении 10 минут"
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    @staticmethod
    @transaction.atomic
    def create_verification_code(
        user: CustomUser,
        expiration_minutes: int = 10,
    ) -> EmailConfirmationCode:
        EmailConfirmationCode.objects.filter(
            user=user, is_used=False, expired_at__gt=timezone.now()
        ).update(is_used=True)

        code = email_confirmation_code_generate()

        verification_code = EmailConfirmationCode.objects.create(
            user=user,
            code=code,
            expired_at=timezone.now() + timedelta(minutes=expiration_minutes),
        )

        return verification_code

    @staticmethod
    def verify_code(email: str, code: str) -> EmailConfirmationCode:
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")
        verification_code = EmailConfirmationCode.objects.filter(
            user=user,
            code=code,
            is_used=False,
            expired_at__gt=timezone.now(),
        ).first()

        if not verification_code:
            raise ValidationError("Invalid code")

        return verification_code
