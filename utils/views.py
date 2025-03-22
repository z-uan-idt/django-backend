from django.db import transaction
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import mixins, views

from drf_yasg.utils import swagger_auto_schema

from utils.mixins.base_api_view_mixin import BaseAPIViewMixin
from utils.mixins.serializer_mixin import GenericViewSetMixin
from utils.api_response import (
    SuccessResponse,
    CreatedResponse,
    NoContentResponse,
    NotFoundResponse,
)


AUTO_SCHEMA_NONE = swagger_auto_schema(auto_schema=None)


@method_decorator(name="list", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="update", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="create", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="destroy", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="retrieve", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="partial_update", decorator=AUTO_SCHEMA_NONE)
class APIGenericView(
    BaseAPIViewMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSetMixin,
):
    """
    View cơ sở cho API Generic
    Hỗ trợ CRUD và các thao tác với model
    """

    permission_classes = []  # Default là không yêu cầu quyền
    permission_action_classes = {}  # Map action -> permissions
    renderer_classes = [JSONRenderer]  # Default renderer

    def get_permissions(self):
        """
        Lấy danh sách permissions dựa trên action hiện tại

        Returns:
            list: Danh sách các permission instance
        """
        if self.action in self.permission_action_classes:
            actions = self.permission_action_classes[self.action]
            return [permission() for permission in actions]

        return [permission() for permission in self.permission_classes]

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Args:
            serializer: Serializer chứa dữ liệu để tạo object

        Returns:
            Model: Object đã được tạo
        """
        instance = serializer.save()
        return instance

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Args:
            serializer: Serializer chứa dữ liệu để cập nhật object

        Returns:
            Model: Object đã được cập nhật
        """
        instance = serializer.save()
        return instance

    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Args:
            instance: Object cần xóa
        """
        # Kiểm tra và thực hiện xóa mềm nếu có hỗ trợ
        if hasattr(instance, "is_delete"):
            instance.delete()  # Xóa mềm
        else:
            super().perform_destroy(instance)  # Xóa cứng

    def list(self, request, *args, **kwargs):
        """
        Override list để tùy chỉnh response
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Kiểm tra xem có cần phân trang không
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return SuccessResponse(data=serializer.data)
        except Exception as e:
            raise

    def create(self, request, *args, **kwargs):
        """
        Override create để tùy chỉnh response
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CreatedResponse(data=serializer.data, headers=headers)
        except Exception as e:
            raise

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve để tùy chỉnh response
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return SuccessResponse(data=serializer.data)
        except ObjectDoesNotExist:
            return NotFoundResponse()
        except Exception as e:
            raise

    def update(self, request, *args, **kwargs):
        """
        Override update để tùy chỉnh response
        """
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return SuccessResponse(data=serializer.data)
        except ObjectDoesNotExist:
            return NotFoundResponse()
        except Exception as e:
            raise

    def partial_update(self, request, *args, **kwargs):
        """
        Override partial_update để tùy chỉnh response
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy để tùy chỉnh response
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return NoContentResponse()
        except ObjectDoesNotExist:
            return NotFoundResponse()
        except Exception as e:
            raise


class APIView(BaseAPIViewMixin, views.APIView):
    """
    View cơ sở cho API thuần
    """

    permission_classes = []  # Default là không yêu cầu quyền
    renderer_classes = [JSONRenderer]  # Default renderer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

    def handle_exception(self, exc):
        """
        Args:
            exc: Exception cần xử lý

        Returns:
            Response: Response sau khi xử lý exception
        """
        return super().handle_exception(exc)


class SecureAPIView(APIView):
    """
    View bảo mật cho API yêu cầu xác thực
    """

    permission_classes = [IsAuthenticated]


class ReadOnlyModelViewSet(
    BaseAPIViewMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSetMixin,
):
    """
    ViewSet chỉ đọc
    """

    def list(self, request, *args, **kwargs):
        """
        Override list để tùy chỉnh response
        """
        response = super().list(request, *args, **kwargs)
        return SuccessResponse(data=response.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve để tùy chỉnh response
        """
        response = super().retrieve(request, *args, **kwargs)
        return SuccessResponse(data=response.data)


class ModelViewSet(APIGenericView):
    """
    ViewSet đầy đủ
    """

    pass
