from django.db.models.query import QuerySet

from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.request import Request

from functools import cached_property
from typing import Any, Dict, Type, Union, List, Optional

from utils.mixins.serializer_mixin import SerializerMixin
from utils.mixins.serializer_mixin import EmptySerializer
from utils.api_response import APIResponse
from utils.paginator import Paginator


class BaseAPIViewMixin(SerializerMixin):
    """
    Mixin view API cơ sở cung cấp chức năng chung cho các view API.

    Mixin này xử lý việc lựa chọn serializer, khởi tạo request,
    định dạng response, phân trang và xử lý ngoại lệ.
    """

    serializer_class: Type[Serializer] = None  # Lớp serializer mặc định
    request: Request = None  # Sẽ được thiết lập bởi Django
    pagination_class = None  # Lớp phân trang
    page_size = 20  # Kích thước trang mặc định

    @cached_property
    def api_response(self) -> Type[APIResponse]:
        """
        Lấy lớp API response để định dạng các response.

        Returns:
            Type[APIResponse]: Lớp APIResponse để tạo response
        """
        return APIResponse

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Lấy ngữ cảnh bổ sung để truyền cho serializers.

        Ghi đè phương thức này để cung cấp ngữ cảnh tùy chỉnh.

        Returns:
            Dict[str, Any]: Context cho serializer
        """
        context = {"request": self.request, "format": self.format_kwarg, "view": self}

        # Thêm thông tin user nếu có
        if hasattr(self.request, "user"):
            context["user"] = self.request.user

        return context

    def get_request_serializer(self, *args, **kwargs) -> Serializer:
        """
        Lấy một request serializer đã khởi tạo với ngữ cảnh phù hợp.

        Args:
            *args: Đối số vị trí để truyền cho serializer
            **kwargs: Đối số từ khóa để truyền cho serializer

        Returns:
            Serializer: Instance serializer đã khởi tạo cho request
        """
        # Lấy lớp serializer phù hợp
        serializer_class = self.get_request_serializer_class() or self.serializer_class

        if not serializer_class:
            serializer_class = EmptySerializer

        # Thiết lập ngữ cảnh
        if "context" not in kwargs:
            kwargs.setdefault("context", {})

        kwargs["context"].update(self.get_serializer_context() or {})

        # Trả về serializer đã khởi tạo
        return serializer_class(*args, **kwargs)

    def get_response_serializer(self, *args, **kwargs) -> Serializer:
        """
        Lấy một response serializer đã khởi tạo với ngữ cảnh phù hợp.

        Args:
            *args: Đối số vị trí để truyền cho serializer
            **kwargs: Đối số từ khóa để truyền cho serializer

        Returns:
            Serializer: Instance serializer đã khởi tạo cho response
        """
        # Lấy lớp serializer phù hợp
        serializer_class = self.get_response_serializer_class() or self.serializer_class

        if not serializer_class:
            serializer_class = EmptySerializer

        # Thiết lập ngữ cảnh
        if "context" not in kwargs:
            kwargs.setdefault("context", {})

        kwargs["context"].update(self.get_serializer_context() or {})

        # Trả về serializer đã khởi tạo
        return serializer_class(*args, **kwargs)

    def get_serializer(self, *args, **kwargs) -> Serializer:
        """
        Lấy serializer phù hợp với action hiện tại.

        Args:
            *args: Đối số vị trí cho serializer
            **kwargs: Đối số từ khóa cho serializer

        Returns:
            Serializer: Instance serializer đã khởi tạo
        """
        # Dựa vào direction để quyết định loại serializer
        is_request = kwargs.pop("is_request", True)

        if is_request:
            return self.get_request_serializer(*args, **kwargs)
        else:
            return self.get_response_serializer(*args, **kwargs)

    def get_serializer_class(self) -> Type[Serializer]:
        """
        Lấy lớp serializer để sử dụng cho tạo schema và tài liệu.

        Returns:
            Type[Serializer]: Lớp serializer để sử dụng cho view này
        """
        serializer_class = self.get_request_serializer_class()

        if serializer_class is None:
            serializer_class = self.serializer_class

        if serializer_class is None:
            # Đánh dấu view này là fake view cho swagger
            setattr(self, "swagger_fake_view", True)
            serializer_class = EmptySerializer

        return serializer_class

    def initialize_request(self, request, *args, **kwargs) -> Request:
        """
        Khởi tạo đối tượng request cho view này.

        Args:
            request: HttpRequest gốc
            *args: Đối số vị trí bổ sung
            **kwargs: Đối số từ khóa bổ sung

        Returns:
            Request: Đối tượng Request đã được khởi tạo
        """
        return super().initialize_request(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs) -> Response:
        """
        Hoàn thiện response, đảm bảo nó được bọc trong một APIResponse.

        Args:
            request: Request đến
            response: Response thô để hoàn thiện
            *args: Đối số vị trí bổ sung
            **kwargs: Đối số từ khóa bổ sung

        Returns:
            Response: Response đã hoàn thiện sẵn sàng gửi đến client
        """
        # Bọc response trong APIResponse nếu cần thiết
        if not isinstance(response, Response):
            response = self.api_response(data=response)

        return super().finalize_response(request, response, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Gửi request đến phương thức xử lý thích hợp.

        Args:
            request: Request đến
            *args: Đối số vị trí bổ sung
            **kwargs: Đối số từ khóa bổ sung

        Returns:
            Response: Response từ handler
        """
        return super().dispatch(request, *args, **kwargs)

    def handle_exception(self, exc):
        """
        Xử lý các ngoại lệ phát sinh trong quá trình xử lý request.

        Args:
            exc: Exception cần xử lý

        Returns:
            Response: Response sau khi xử lý exception
        """
        return super().handle_exception(exc)

    def paginator(
        self,
        object_list: Union[List, QuerySet],
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """
        Phân trang danh sách đối tượng.

        Args:
            object_list: Danh sách cần phân trang
            per_page: Số lượng item trên mỗi trang
            page: Số trang
            **kwargs: Tham số bổ sung

        Returns:
            Dict: Kết quả đã phân trang
        """
        # Lấy serializer cho response
        response_serializer = self.get_response_serializer

        # Lấy thông tin trang từ request nếu chưa được chỉ định
        if page is None:
            page = Paginator.from_request(self.request, "page")

        if per_page is None:
            per_page = Paginator.from_request(self.request, "limit") or self.page_size

        # Tạo paginator và phân trang
        _paginator = Paginator(object_list, per_page)
        _paginator = _paginator.page(page)
        _paginator = _paginator.set_results_classes(response_serializer, option=kwargs)

        output_results = _paginator.output_results

        return self.api_response(
            data=output_results.pop("results", []),
            metadata={"pagination": output_results},
        )
