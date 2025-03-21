from django.http import JsonResponse

from rest_framework.response import Response

from typing import Any, Union, List, Tuple, Dict
import time

from constants import AppMode
from constants.http_status_code import HttpStatusCode
from constants.response_messages import ResponseMessage


class BaseAPIResponse:
    """
    Lớp cơ sở định nghĩa cấu trúc response API
    """

    def build_response(
        self,
        data: Any = None,
        message: str = None,
        success: bool = None,
        status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
        errors: Union[List, Tuple, Dict, None] = None,
        metadata: Dict = None,
    ) -> Dict:
        """
        Tạo cấu trúc response chuẩn

        Args:
            data: Dữ liệu trả về
            message: Thông báo
            success: Trạng thái thành công
            status: Mã status HTTP
            errors: Thông tin lỗi (nếu có)
            metadata: Metadata bổ sung (nếu có)

        Returns:
            Dict: Response đã được cấu trúc
        """
        # Chuyển đổi status thành HttpStatusCode nếu là int
        status = HttpStatusCode(status) if isinstance(status, int) else status

        # Xác định success dựa trên status nếu không được chỉ định
        success = (
            success if success is not None else HttpStatusCode.is_success(status.value)
        )

        # Xác định message nếu không được chỉ định
        message = message or getattr(ResponseMessage, status.name.upper(), "").value

        # Cấu trúc response cơ bản
        response_structure = {
            "status": status.value,
            "success": success,
            "status_text": status.name,
            "message": message,
            "timestamp": int(time.time()),
            "data": data,
            "metadata": metadata,
        }

        # Thêm errors nếu có
        if errors is not None and AppMode.DEBUG:
            response_structure["errors"] = errors

        return response_structure


class APIResponse(Response, BaseAPIResponse):
    """
    Response API cho DRF
    """

    def __init__(
        self,
        data: Any = None,
        message: str = None,
        success: bool = None,
        http_status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
        status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
        errors: Union[List, Tuple, Dict, None] = None,
        metadata: Dict = None,
        **kwargs
    ):
        """
        Khởi tạo response API

        Args:
            data: Dữ liệu trả về
            message: Thông báo
            success: Trạng thái thành công
            http_status: Mã status HTTP trả về trong header
            status: Mã status trong nội dung response
            errors: Thông tin lỗi (nếu có)
            metadata: Metadata bổ sung (nếu có)
            **kwargs: Các tham số khác cho Response
        """
        response_data = self.build_response(
            data, message, success, status, errors, metadata
        )
        http_status = (
            HttpStatusCode(http_status) if isinstance(http_status, int) else http_status
        )

        super().__init__(data=response_data, status=http_status.value, **kwargs)


class JsonAPIResponse(JsonResponse, BaseAPIResponse):
    """
    Response API cho Django JSON Response
    """

    def __init__(
        self,
        data: Any = None,
        message: str = None,
        success: bool = None,
        status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
        errors: Union[List, Tuple, Dict, None] = None,
        metadata: Dict = None,
        **kwargs
    ):
        """
        Khởi tạo JSON response API

        Args:
            data: Dữ liệu trả về
            message: Thông báo
            success: Trạng thái thành công
            status: Mã status HTTP
            errors: Thông tin lỗi (nếu có)
            metadata: Metadata bổ sung (nếu có)
            **kwargs: Các tham số khác cho JsonResponse
        """
        response_data = self.build_response(
            data, message, success, status, errors, metadata
        )

        super().__init__(data=response_data, **kwargs)


class SuccessResponse(APIResponse):
    """
    Response API thành công
    """

    def __init__(
        self, data: Any = None, message: str = ResponseMessage.OK.value, **kwargs
    ):
        super().__init__(data=data, message=message, status=HttpStatusCode.OK, **kwargs)


class CreatedResponse(APIResponse):
    """
    Response API tạo thành công
    """

    def __init__(
        self, data: Any = None, message: str = ResponseMessage.CREATED.value, **kwargs
    ):
        super().__init__(
            data=data, message=message, status=HttpStatusCode.CREATED, **kwargs
        )


class NoContentResponse(APIResponse):
    """
    Response API không có nội dung
    """

    def __init__(self, message: str = ResponseMessage.NO_CONTENT.value, **kwargs):
        super().__init__(
            data=None, message=message, status=HttpStatusCode.NO_CONTENT, **kwargs
        )


class BadRequestResponse(APIResponse):
    """
    Response API lỗi bad request
    """

    def __init__(
        self,
        message: str = ResponseMessage.BAD_REQUEST.value,
        errors: Union[List, Tuple, Dict, None] = None,
        **kwargs
    ):
        super().__init__(
            data=None,
            message=message,
            status=HttpStatusCode.BAD_REQUEST,
            errors=errors,
            **kwargs
        )


class NotFoundResponse(APIResponse):
    """
    Response API lỗi không tìm thấy
    """

    def __init__(self, message: str = ResponseMessage.NOT_FOUND.value, **kwargs):
        super().__init__(
            data=None, message=message, status=HttpStatusCode.NOT_FOUND, **kwargs
        )


class UnauthorizedResponse(APIResponse):
    """
    Response API lỗi không có quyền truy cập
    """

    def __init__(self, message: str = ResponseMessage.UNAUTHORIZED.value, **kwargs):
        super().__init__(
            data=None, message=message, status=HttpStatusCode.UNAUTHORIZED, **kwargs
        )


class ForbiddenResponse(APIResponse):
    """
    Response API lỗi cấm truy cập
    """

    def __init__(self, message: str = ResponseMessage.FORBIDDEN.value, **kwargs):
        super().__init__(
            data=None, message=message, status=HttpStatusCode.FORBIDDEN, **kwargs
        )


class ConflictResponse(APIResponse):
    """
    Response API lỗi xung đột dữ liệu
    """

    def __init__(self, message: str = ResponseMessage.CONFLICT.value, **kwargs):
        super().__init__(
            data=None, message=message, status=HttpStatusCode.CONFLICT, **kwargs
        )


class TooManyRequestsResponse(APIResponse):
    """
    Response API lỗi quá nhiều yêu cầu
    """

    def __init__(
        self, message: str = ResponseMessage.TOO_MANY_REQUESTS.value, **kwargs
    ):
        super().__init__(
            data=None,
            message=message,
            status=HttpStatusCode.TOO_MANY_REQUESTS,
            **kwargs
        )


class ServerErrorResponse(APIResponse):
    """
    Response API lỗi server
    """

    def __init__(
        self, message: str = ResponseMessage.INTERNAL_SERVER_ERROR.value, **kwargs
    ):
        super().__init__(
            data=None,
            message=message,
            status=HttpStatusCode.INTERNAL_SERVER_ERROR,
            **kwargs
        )
