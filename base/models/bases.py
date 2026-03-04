from django.db import models


class BaseModelID(models.Model):
    class Meta:
        ordering = ("-id",)
        abstract = True

    id = models.BigAutoField("ID", primary_key=True, editable=True)

    def __str__(self) -> str:
        return f"*{self.pk}"


class BaseModelIDTime(BaseModelID):
    class Meta:
        ordering = ("-created_at",)
        abstract = True

    created_at = models.DateTimeField("created_at", auto_now_add=True)
    updated_at = models.DateTimeField("updated_at", auto_now=True)


__all__ = [
    "BaseModelID",
    "BaseModelIDTime",
]
