from functools import partial
from typing import Any, Callable, Optional, Protocol

from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_json_api.views import (
    AutoPrefetchMixin,
    PreloadIncludesMixin,
    RelatedMixin,
)

from account.models.users import CustomUser


class BaseViewSet(
    viewsets.GenericViewSet,
    RelatedMixin,
    PreloadIncludesMixin,
    AutoPrefetchMixin,
):
    # permission_classes = []
    http_method_names = ["get", "post", "patch", "delete", "options"]

    def get_extra_serializer_context(self) -> dict:
        user: CustomUser = self.request.user  # type: ignore
        return {"user": user}

    def get_serializer_context(self):
        if self.request.method in ["HEAD", "OPTIONS"]:
            return super().get_serializer_context()
        else:
            return (
                super().get_serializer_context() | self.get_extra_serializer_context()
            )

    def post_update_function(
        self, instance, **kwargs
    ) -> tuple[Optional[Callable], dict]:
        return (None, {})

    def post_update_action(self, instance, **kwargs):
        f, data = self.post_update_function(instance, **kwargs)
        if f is not None:
            transaction.on_commit(partial(f, **data))

    def post_create_function(
        self, instance, **kwargs
    ) -> tuple[Optional[Callable], dict]:
        return (None, {})

    def post_create_action(self, instance, **kwargs):
        f, data = self.post_create_function(instance, **kwargs)
        if f is not None:
            transaction.on_commit(partial(f, **data))

    def perform_update_kwargs(self) -> dict:
        return {}

    def perform_update(self, serializer):
        instance = serializer.save(**self.perform_update_kwargs())
        self.post_update_action(instance)
        return instance

    def perform_create_kwargs(self) -> dict:
        return {}

    def perform_create(self, serializer):
        try:
            instance = serializer.save(**self.perform_create_kwargs())
        except IntegrityError as e:
            raise ValidationError()
        except:
            raise
        self.post_create_action(instance)
        return instance

    def post_destroy_function(
        self, instance, **kwargs
    ) -> tuple[Optional[Callable], dict]:
        return (None, {})

    def post_destroy_action(self, instance, **kwargs):
        f, data = self.post_destroy_function(instance, **kwargs)
        if f is not None:
            transaction.on_commit(partial(f, **data))

    def perform_destroy(self, instance):
        instance.delete()
        self.post_destroy_action(instance)


class ViewProtocol(Protocol):
    def get_object(self, *args, **kwargs) -> Any: ...
    def get_serializer(self, *args, **kwargs) -> Any: ...
    def perform_create(self, *args, **kwargs) -> Any: ...
    def filter_queryset(self, *args, **kwargs) -> Any: ...
    def get_queryset(self, *args, **kwargs) -> Any: ...
    def paginate_queryset(self, *args, **kwargs) -> Any: ...
    def get_paginated_response(self, *args, **kwargs) -> Any: ...


class CreateModelMixin(ViewProtocol):
    def create_endpoint(
        self,
        request,
        *args,
        response_serializer_class=None,
        status=status.HTTP_201_CREATED,
        response_many: bool = False,
        **kwargs,
    ):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if response_serializer_class is None:
            return Response(serializer.data, status=status)
        else:
            return Response(
                response_serializer_class(
                    serializer.instance, context=serializer.context, many=response_many
                ).data,
                status=status,
            )

    def perform_create(self, serializer):
        serializer.save()


class ListModelMixin(ViewProtocol):
    def list_endpoint(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveModelMixin(ViewProtocol):
    def retrieve_endpoint(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UpdateModelMixin(ViewProtocol):
    def update_endpoint(
        self,
        request,
        *args,
        partial: bool = True,
        response_serializer_class=None,
        status=status.HTTP_200_OK,
        **kwargs,
    ):
        partial = kwargs.pop("partial", partial)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        if response_serializer_class is None:
            return Response(serializer.data, status=status)
        else:
            return Response(
                response_serializer_class(
                    serializer.instance, context=serializer.context
                ).data,
                status=status,
            )

    def perform_update(self, serializer):
        serializer.save()


class DestroyModelMixin(ViewProtocol):
    def destroy_endpoint(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
