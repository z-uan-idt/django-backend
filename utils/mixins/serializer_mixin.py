from rest_framework.serializers import Serializer
from rest_framework.exceptions import NotFound
from rest_framework import viewsets

from typing import Dict, Type, Optional

from constants.response_messages import ResponseMessage


class EmptySerializer(Serializer):
    """
    Serializer rỗng để sử dụng khi không có serializer cụ thể
    """

    def update(self, instance, validated_data):
        """
        Method update rỗng cho EmptySerializer

        Args:
            instance: Đối tượng cần cập nhật
            validated_data: Dữ liệu đã được xác thực

        Returns:
            None
        """
        pass

    def create(self, validated_data):
        """
        Method create rỗng cho EmptySerializer

        Args:
            validated_data: Dữ liệu đã được xác thực

        Returns:
            None
        """
        pass


class SerializerMixin(object):
    """
    Mixin cung cấp khả năng sử dụng nhiều serializer khác nhau cho từng action
    """

    request_serializer_class = None  # Serializer cho request
    response_serializer_class = None  # Serializer cho response
    action_serializers: Dict[str, Type[Serializer]] = {}  # Map action -> serializer

    def get_serializer_for_action(
        self, action: str, for_request: bool = True
    ) -> Optional[Type[Serializer]]:
        """
        Lấy serializer phù hợp cho từng action với cơ chế fallback hợp lý

        Args:
            action: Tên action cần lấy serializer
            for_request: True nếu cần serializer cho request, False nếu cho response

        Returns:
            Type[Serializer]: Lớp serializer phù hợp hoặc None nếu không tìm thấy
        """
        suffix = "_request" if for_request else "_response"
        action_key = action + suffix

        # Thử tìm action specific serializer
        if action_key in self.action_serializers:
            return self.action_serializers.get(action_key)

        # Thử dùng action serializer không có hậu tố
        if action in self.action_serializers:
            return self.action_serializers.get(action)

        # Fallback theo request/response
        if for_request and self.request_serializer_class:
            return self.request_serializer_class
        elif not for_request and self.response_serializer_class:
            return self.response_serializer_class

        # Cuối cùng, dùng serializer mặc định
        return self.serializer_class

    def get_request_serializer_class(self) -> Optional[Type[Serializer]]:
        """
        Lấy lớp serializer cho request

        Returns:
            Type[Serializer]: Lớp serializer cho request hoặc None
        """
        if hasattr(self, "action"):
            return self.get_serializer_for_action(self.action, for_request=True)

    def get_response_serializer_class(self) -> Optional[Type[Serializer]]:
        """
        Lấy lớp serializer cho response

        Returns:
            Type[Serializer]: Lớp serializer cho response hoặc None
        """
        if hasattr(self, "action"):
            return self.get_serializer_for_action(self.action, for_request=False)


class GenericViewSetMixin(viewsets.GenericViewSet):
    """
    Mixin cung cấp khả năng sử dụng nhiều queryset khác nhau cho từng action
    """

    action_query_sets = {}  # Map action -> queryset
    action_filtering = {}  # Map action -> filter functions
    default_error_messages = {
        "not_found": "Không tìm thấy dữ liệu yêu cầu.",
        "no_queryset": "Không có queryset được cấu hình cho view này.",
    }

    def get_queryset(self):
        """
        Lấy queryset phù hợp cho action hiện tại

        Returns:
            QuerySet: Queryset phù hợp cho action hiện tại

        Raises:
            NotFound: Nếu không tìm thấy queryset phù hợp
        """
        # Bỏ qua nếu đang trong swagger fake view
        if getattr(self, "swagger_fake_view", False):
            return None

        # Lấy queryset cho action cụ thể
        if self.action in self.action_query_sets:
            queryset = self.action_query_sets.get(self.action)

            # Áp dụng filter cho action nếu có
            if self.action in self.action_filtering:
                filter_func = self.action_filtering[self.action]
                queryset = filter_func(queryset, self.request)

            return queryset

        # Fallback về queryset mặc định
        if getattr(self, "queryset", None) is not None:
            queryset = super().get_queryset()

            # Áp dụng filter cho tất cả actions nếu có
            if "*" in self.action_filtering:
                filter_func = self.action_filtering["*"]
                queryset = filter_func(queryset, self.request)

            return queryset

        raise NotFound(ResponseMessage.NOT_FOUND)

    def filter_queryset(self, queryset):
        """
        Áp dụng các filter backend lên queryset

        Args:
            queryset: Queryset cần lọc

        Returns:
            QuerySet: Queryset đã được lọc
        """
        # Áp dụng các filter backend
        filtered_queryset = super().filter_queryset(queryset)

        # Log thông tin
        if filtered_queryset is not queryset:
            original_count = queryset.count() if hasattr(queryset, "count") else "?"
            filtered_count = (
                filtered_queryset.count()
                if hasattr(filtered_queryset, "count")
                else "?"
            )

        return filtered_queryset
