from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from account.api.auth.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
)
from account.models.users import CustomUser


class NoJSONAPIRendererMixin:
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]


class JWTTokenObtainPairView(NoJSONAPIRendererMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.none()
    authentication_classes = ()
    serializer_class = TokenObtainPairSerializer

    @extend_schema(
        summary="Получение access и refresh токенов",
        description="""Возвращает пару access и refresh токенов для аутентификации""",
        tags=["Аутентификация"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTTokenRefreshView(NoJSONAPIRendererMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.none()
    authentication_classes = ()
    serializer_class = TokenRefreshSerializer

    @extend_schema(
        summary="Получение access токена по refrsh",
        description="""Возвращает access токен по refresh токену.""",
        tags=["Аутентификация"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTTokenVerifyView(NoJSONAPIRendererMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.none()
    authentication_classes = ()
    serializer_class = TokenVerifySerializer

    @extend_schema(
        summary="Верификация пользователя",
        description="""Возвращает сообщение с ответом ок и id пользователя.""",
        tags=["Аутентификация"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


__all__ = [
    "JWTTokenObtainPairView",
    "JWTTokenRefreshView",
    "JWTTokenVerifyView",
]
