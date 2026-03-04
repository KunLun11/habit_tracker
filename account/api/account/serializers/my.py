from rest_framework_json_api import serializers

from account.models.users import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "email",
            "phone",
            "is_active",
            "first_name",
            "last_name",
        )
        model = CustomUser


__all__ = [
    "CustomUserSerializer",
]
