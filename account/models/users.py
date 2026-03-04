from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

from base.models.bases import BaseModelIDTime


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(BaseModelIDTime, AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "Пользователь API"
        verbose_name_plural = "Пользователи API"

    username = None

    email = models.EmailField("Email адрес", unique=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    date_joined = models.DateTimeField("Дата входа", default=timezone.now)

    email_activated = models.BooleanField(
        "Почта активирована", default=True, blank=True
    )
    phone_activated = models.BooleanField(
        "Номер телефона активирован", default=True, blank=True
    )
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)

    is_staff = models.BooleanField(
        "Статус сотрудника",
        default=False,
        help_text="Может ли пользователь входить в админку",
    )
    is_active = models.BooleanField(
        "Активный", default=True, help_text="Аккаунт активен или заблокирован"
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


__all__ = [
    "CustomUser",
]
