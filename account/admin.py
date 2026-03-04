from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from account.models.users import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    # form = UserChangeForm
    # add_form = UserCreationForm
    # change_password_form = AdminPasswordChangeForm

    list_display = (
        "email",
        "phone",
        # "full_name_display",
        "is_active",
        "is_staff",
        "is_superuser",
        "email_activated",
        "phone_activated",
        "date_joined",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "email_activated",
        "phone_activated",
        ("date_joined", admin.DateFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "email",
        "phone",
        "first_name",
        "last_name",
    )

    ordering = ("-created_at", "-date_joined")

    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    )

    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (_("Учетные данные"), {"fields": ("email", "password")}),
        (
            _("Персональная информация"),
            {"fields": ("first_name", "last_name", "phone")},
        ),
        (
            _("Статусы активации"),
            {
                "fields": ("email_activated", "phone_activated"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Права доступа"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Важные даты"),
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (
            _("Персональная информация"),
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "phone"),
            },
        ),
        (
            _("Права доступа"),
            {
                "classes": ("wide",),
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
    )
    # actions_row = [
    #     "get_jwt_access",
    # ]
    # TODO: Получение токена


admin.site.unregister(Group)


@admin.register(Group)
class Group(BaseGroupAdmin, ModelAdmin):
    pass
