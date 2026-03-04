from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from account.api.view_bases import BaseViewSet, CreateModelMixin, ListModelMixin
from habit.api.serializers.habits import (
    HabitCheckinSerializer,
    HabitCreateSerializer,
    HabitListSerializer,
    HabitLogSerializer,
)
from habit.models.habits import Habit, HabitLog


class HabitViewSet(
    BaseViewSet,
    ListModelMixin,
    CreateModelMixin,
):
    queryset = Habit.objects.filter()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create_kwargs(self):
        return {"user": self.request.user}

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_serializer_class(self):
        if self.action == "list":
            return HabitListSerializer
        elif self.action == "create":
            return HabitCreateSerializer
        elif self.action == "checkin":
            return HabitCheckinSerializer
        else:
            HabitListSerializer

    @extend_schema(
        summary="Список привычек",
        description="""Метод позволяет просмотреть список привычек""",
        tags=["Привычки"],
        responses=HabitCheckinSerializer(),
    )
    def list(self, request, *args, **kwargs):
        return self.list_endpoint(request, *args, **kwargs)

    @extend_schema(
        summary="Создание привычки",
        description="""Метод позволяет создать привычку""",
        tags=["Привычки"],
        responses=HabitCheckinSerializer(),
    )
    def create(self, request, *args, **kwargs):
        return self.create_endpoint(
            request, *args, response_serializer_class=HabitListSerializer, **kwargs
        )

    @extend_schema(
        summary="Отметка выполнения привычки",
        description="""Метод позволяет отметить привычку""",
        tags=["Привычки"],
        request=HabitCheckinSerializer,
        responses=HabitCheckinSerializer,
    )
    @action(
        detail=True,
        methods=["POST"],
        serializer_class=HabitCheckinSerializer,
    )
    def checkin(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HabitLogViewSet(BaseViewSet, ListModelMixin):
    queryset = HabitLog.objects.filter()
    serializer_class = HabitLogSerializer

    def get_queryset(self):
        return self.queryset.filter(habit__user=self.request.user)

    def list(self, request, *args, **kwargs):
        return self.list_endpoint(request, *args, **kwargs)
    
