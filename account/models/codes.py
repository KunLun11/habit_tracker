from django.db import models
from django.utils import timezone


class EmailConfirmationCode(models.Model):
    class Meta:
        verbose_name = "Код подтверждения (email)"
        verbose_name_plural = "Коды подтверждения (email)"

    expired_at = models.DateTimeField("Истекает", null=True, blank=True)

    user = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="confirmation_codes",
    )
    code = models.CharField("Код", max_length=14)
    is_used = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
