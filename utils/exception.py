from django.http import Http404
from django.core.exceptions import (
    PermissionDenied,
    ImproperlyConfigured,
    SuspiciousOperation,
    ObjectDoesNotExist,
    DisallowedRedirect,
    FieldDoesNotExist,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import (
    IntegrityError,
    DataError,
    DatabaseError,
    OperationalError,
    ProgrammingError,
    NotSupportedError,
    InternalError,
)
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.db import connections, transaction

from rest_framework.exceptions import (
    NotFound,
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    MethodNotAllowed,
    ParseError,
    UnsupportedMediaType,
    APIException,
)
from rest_framework.views import exception_handler

from typing import Union, Dict, Any
import logging
import traceback
import json
import sys

from constants import AppMode
from constants.http_status_code import HttpStatusCode
from constants.response_messages import ResponseMessage

from utils.api_response import JsonAPIResponse
from utils.api_response import APIResponse
from helpers import bigger, get_client_ip


logger = logging.getLogger("django.exception")
request_logger = logging.getLogger("django.request")


class MessageError(APIException):
    """
    Exception chung cho các lỗi có message cụ thể
    """

    status_code = HttpStatusCode.BAD_REQUEST.value
    default_code = HttpStatusCode.BAD_REQUEST.name
    default_detail = ResponseMessage.BAD_REQUEST

    def __init__(
        self, detail: Union[ResponseMessage, str] = None, status_code: int = None
    ):
        if isinstance(detail, ResponseMessage):
            self.detail = detail.value
        elif isinstance(detail, str) and detail:
            msg_key = detail.upper()
            if hasattr(ResponseMessage, msg_key):
                self.detail = getattr(ResponseMessage, msg_key).value
            else:
                self.detail = detail

        if status_code is not None:
            self.status_code = status_code


class ValidationDetailError(ValidationError):
    """
    Lớp ValidationError tùy chỉnh để có thể chứa thông tin chi tiết về lỗi
    """

    def __init__(self, detail=None, field=None, code=None):
        super().__init__(detail=detail, code=code)
        self.field = field


class ExceptionMiddleware(MiddlewareMixin):
    def should_log_request(self, request):
        EXCLUDED_PATHS = [
            "/favicon.ico",
            "/robots.txt",
            "/manifest.json",
            "/apple-touch-icon.png",
        ]
        return request.path not in EXCLUDED_PATHS and not any(
            request.path.startswith(path) for path in EXCLUDED_PATHS
        )

    def process_response(self, request, response):
        """
        Xử lý response trước khi trả về cho người dùng
        """

        status_code = response.status_code
        try:
            status_code = response.data["status"]
        except:
            pass

        _extra = {
            "request": request,
            "method": request.method,
            "status_code": status_code,
            "client_ip": get_client_ip(request),
            "http_version": "HTTPS/1.1" if request.is_secure() else "HTTP/1.1",
        }

        if request.path == "/admin":
            return redirect("/admin/")

        if HttpStatusCode.is_success(status_code):
            request_logger.info(None, extra=_extra)

        if request.path.startswith("/admin/"):
            request_logger.info(None, extra=_extra)
            return response

        # Xử lý lỗi server (500)
        if HttpStatusCode.is_server_error(response.status_code):
            if self.should_log_request(request):
                request_logger.error(None, extra=_extra)
            return JsonAPIResponse(status=HttpStatusCode.INTERNAL_SERVER_ERROR)

        # Xử lý lỗi không tìm thấy trang (404)
        if response.status_code == HttpStatusCode.NOT_FOUND.value:
            if self.should_log_request(request):
                request_logger.error(None, extra=_extra)
            return JsonAPIResponse(status=HttpStatusCode.NOT_FOUND)

        return response


def get_error_content(exc) -> Any:
    """
    Phân tích nội dung lỗi từ exception.

    Args:
        exc: Exception cần phân tích

    Returns:
        Any: Nội dung lỗi đã được phân tích
    """
    # Xử lý exception dạng dict
    if isinstance(exc, dict):
        if "non_field_errors" in exc:
            return get_error_content(exc["non_field_errors"])

        errors = {}
        for k, v in exc.items():
            errors[k] = get_error_content(v)
        return errors

    # Xử lý exception dạng list
    if isinstance(exc, list):
        if bigger(exc):
            return exc[0]
        return None

    # Xử lý exception có thuộc tính detail
    if hasattr(exc, "detail"):
        return get_error_content(exc.detail)

    if isinstance(exc, DjangoValidationError):
        return get_error_content(exc.message_dict)

    # Fallback
    return str(exc)


def parse_validation_errors(validation_error, prefix="") -> Dict[str, str]:
    """
    Phân tích lỗi validation và chuyển đổi thành định dạng phẳng với các keys được nối bằng __

    Args:
        validation_error: ValidationError cần phân tích
        prefix: Tiền tố để thêm vào trước các keys (dùng cho đệ quy)

    Returns:
        Dict[str, str]: Dict phẳng chứa thông tin lỗi validation
    """
    error_details = {}

    validation_error_detail = getattr(validation_error, "detail", validation_error)

    if not validation_error_detail:
        return {prefix.rstrip("__"): ResponseMessage.INTERNAL_SERVER_ERROR.value}

    if isinstance(validation_error_detail, dict):
        for field, errors in validation_error_detail.items():
            current_prefix = f"{prefix}{field}__" if prefix else f"{field}__"

            if isinstance(errors, list):
                # Kiểm tra xem trong list có dict không
                has_dict = any(isinstance(error, dict) for error in errors)

                if has_dict:
                    # Xử lý trường hợp list chứa dict
                    for i, error in enumerate(errors):
                        if isinstance(error, dict):
                            nested_errors = parse_validation_errors(
                                error, f"{current_prefix}{i}__"
                            )
                            error_details.update(nested_errors)
                        else:
                            error_value = (
                                getattr(error, "detail", error)
                                if error
                                else ResponseMessage.INTERNAL_SERVER_ERROR.value
                            )
                            error_details[f"{current_prefix}{i}"] = str(error_value)
                else:
                    # List cơ bản chỉ chứa lỗi string
                    if errors:
                        error_value = getattr(errors[0], "detail", errors[0])
                        error_details[current_prefix.rstrip("__")] = str(error_value)
                    else:
                        error_details[
                            current_prefix.rstrip("__")
                        ] = ResponseMessage.INTERNAL_SERVER_ERROR.value
            elif isinstance(errors, dict):
                # Đệ quy xử lý dict lồng nhau
                nested_errors = parse_validation_errors(errors, current_prefix)
                error_details.update(nested_errors)
            else:
                # Giá trị đơn
                error_details[current_prefix.rstrip("__")] = str(errors)
    elif isinstance(validation_error_detail, list):
        # Kiểm tra xem trong list có dict không
        has_dict = any(isinstance(error, dict) for error in validation_error_detail)

        if has_dict:
            for i, error in enumerate(validation_error_detail):
                if isinstance(error, dict):
                    current_prefix = f"{prefix}{i}__" if prefix else f"{i}__"
                    nested_errors = parse_validation_errors(error, current_prefix)
                    error_details.update(nested_errors)
                else:
                    field_name = (
                        f"{prefix}non_field_errors" if prefix else "non_field_errors"
                    )
                    error_details[field_name] = str(error)
        else:
            field_name = f"{prefix}non_field_errors" if prefix else "non_field_errors"
            if validation_error_detail:
                error_details[field_name] = str(validation_error_detail[0])
            else:
                error_details[field_name] = ResponseMessage.INTERNAL_SERVER_ERROR.value
    else:
        # Giá trị đơn
        field_name = prefix.rstrip("__") if prefix else "detail"
        error_details[field_name] = str(validation_error_detail)

    return error_details


def get_simplified_traceback(limit: int = 8) -> str:
    """
    Tạo traceback đơn giản hóa và dễ đọc hơn

    Args:
        limit: Số lượng dòng traceback tối đa

    Returns:
        str: Traceback đã được đơn giản hóa
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(
        exc_type, exc_value, exc_traceback, limit=limit
    )

    # Bỏ bớt thông tin không cần thiết và rút gọn đường dẫn
    simplified_lines = []
    for line in tb_lines:
        if "site-packages" in line:
            # Rút gọn đường dẫn từ thư viện bên ngoài
            parts = line.split("site-packages/")
            if bigger(parts, 1):
                line = parts[0] + "site-packages/" + parts[1].split("/")[-1]
        simplified_lines.append(line)

    return "".join(simplified_lines).strip()


def get_meaningful_traceback(simplified_traceback, initial_slice=10):
    """
    Lấy phần traceback có ý nghĩa

    :param simplified_traceback: Chuỗi traceback đầy đủ
    :param initial_slice: Số dòng ban đầu muốn lấy
    :return: Danh sách các dòng traceback
    """
    # Tách traceback thành các dòng
    _traceback = simplified_traceback.split("\n")

    # Nếu tổng số dòng nhỏ hơn slice ban đầu, trả về toàn bộ
    if len(_traceback) <= initial_slice:
        return _traceback

    # Thử với slice ban đầu
    sliced_traceback = _traceback[-initial_slice:]

    # Nếu dòng đầu tiên không chứa 'Traceback', tăng slice
    while not any("Traceback" in line for line in sliced_traceback):
        initial_slice += 5

        # Nếu slice vượt quá tổng số dòng, trả về toàn bộ
        if initial_slice >= len(_traceback):
            return _traceback

        sliced_traceback = _traceback[-initial_slice:]

    return sliced_traceback


def ExceptionHandler(exc, context):
    """
    Xử lý toàn bộ exception trong dự án và trả về response có định dạng nhất quán.

    Args:
        exc: Exception cần xử lý
        context: Context của request

    Returns:
        APIResponse: Response với định dạng nhất quán
    """
    # Lấy request từ context
    request = context.get("request", None)

    # Lấy DRF exception handler gốc
    exc_response = exception_handler(exc, context)

    # Xác định status code mặc định
    status_code = getattr(exc, "status_code", HttpStatusCode.BAD_REQUEST.value)
    try:
        status = HttpStatusCode(status_code)
    except ValueError:
        # Nếu status code không hợp lệ, sử dụng BAD_REQUEST
        status = HttpStatusCode.BAD_REQUEST

    # Lấy traceback đơn giản hóa
    simplified_traceback = get_simplified_traceback()

    http_version = "HTTPS/1.1" if request.is_secure() else "HTTP/1.1"

    _traceback = []
    if status_code not in (
        HttpStatusCode.UNAUTHORIZED.value,
        HttpStatusCode.FORBIDDEN.value,
    ):
        _traceback = get_meaningful_traceback(simplified_traceback)

    def format_traceback(_value):
        if not _value:
            return ""

        formatted_value = _value.copy()

        formatted_value[-1] = f"└── {formatted_value[-1]}"

        formatted_value[:-1] = [f"├── {item}" for item in formatted_value[:-1]]

        return "\n         ".join(formatted_value)

    short_traceback = (":\n         " + format_traceback(_traceback)) if _traceback else ""
    logger.error(
        f'"{request.method} {request.get_full_path()} {http_version}" {status_code}{short_traceback}',
        extra={
            "request": request,
            "method": request.method,
            "status_code": status_code,
            "http_version": http_version,
            "client_ip": get_client_ip(request),
            "simplified_traceback": short_traceback,
        },
    )

    # Xử lý các loại exception cụ thể một cách chi tiết hơn
    if isinstance(exc, (Http404, ObjectDoesNotExist, NotFound, FieldDoesNotExist)):
        status = HttpStatusCode.NOT_FOUND
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        status = HttpStatusCode.UNAUTHORIZED
    elif isinstance(exc, PermissionDenied):
        status = HttpStatusCode.FORBIDDEN
    elif isinstance(exc, (ValidationError, DjangoValidationError)):
        status = HttpStatusCode.BAD_REQUEST
    elif isinstance(exc, MethodNotAllowed):
        status = HttpStatusCode.METHOD_NOT_ALLOWED
    elif isinstance(exc, UnsupportedMediaType):
        status = HttpStatusCode.UNSUPPORTED_MEDIA_TYPE
    elif isinstance(exc, ParseError):
        status = HttpStatusCode.BAD_REQUEST
    elif isinstance(exc, IntegrityError):
        status = HttpStatusCode.CONFLICT
    elif isinstance(
        exc,
        (
            DataError,
            DatabaseError,
            OperationalError,
            ProgrammingError,
            NotSupportedError,
            InternalError,
        ),
    ):
        status = HttpStatusCode.BAD_REQUEST
    elif isinstance(exc, transaction.TransactionManagementError):
        status = HttpStatusCode.INTERNAL_SERVER_ERROR
    elif isinstance(exc, ImproperlyConfigured):
        status = HttpStatusCode.INTERNAL_SERVER_ERROR
    elif isinstance(exc, (SuspiciousOperation, DisallowedRedirect)):
        status = HttpStatusCode.BAD_REQUEST
    elif isinstance(exc, json.JSONDecodeError):
        status = HttpStatusCode.BAD_REQUEST
    elif exc_response is None:
        status = HttpStatusCode.INTERNAL_SERVER_ERROR

    # Rollback transaction nếu cần
    for db in connections.all():
        if db.settings_dict.get("ATOMIC_REQUESTS", False) and db.in_atomic_block:
            db.set_rollback(True)

    # Lấy message dựa trên status
    status_name = status.name.upper()
    message = getattr(ResponseMessage, status_name, ResponseMessage.BAD_REQUEST).value

    # Chuẩn bị response
    response_kwargs = {
        "status": status,
        "message": message,
        "errors": {
            "code": status.value,
            "type": exc.__class__.__name__,
            "error": get_error_content(exc),
        },
    }

    # Xử lý đặc biệt cho một số loại exception
    if isinstance(exc, MessageError):
        response_kwargs["message"] = exc.detail
        response_kwargs["errors"] = None
    elif isinstance(exc, NotFound):
        response_kwargs["message"] = getattr(
            exc, "detail", ResponseMessage.NOT_FOUND.value
        )
        response_kwargs["errors"] = None

    if isinstance(exc, ValidationError) and hasattr(exc, "detail"):
        # Cung cấp thông tin chi tiết hơn cho lỗi validation
        error_details = parse_validation_errors(exc)
        response_kwargs["errors"]["fields"] = error_details

        if isinstance(error_details, dict) and error_details:
            first_key = next(iter(error_details.keys()), None)
            if first_key is not None:
                # Lấy thông báo lỗi từ key đầu tiên
                response_kwargs["message"] = error_details[first_key]
    elif isinstance(exc, DjangoValidationError):
        # Cung cấp thông tin chi tiết hơn cho lỗi validation
        error_details = parse_validation_errors(get_error_content(exc))

        if isinstance(error_details, dict) and error_details:
            first_key = next(iter(error_details.keys()), None)
            if first_key is not None:
                # Lấy thông báo lỗi từ key đầu tiên
                response_kwargs["message"] = error_details[first_key]

    # Xử lý trường hợp lỗi ValidationDetailError riêng biệt
    if isinstance(exc, ValidationDetailError) and hasattr(exc, "field"):
        error_details = parse_validation_errors(exc)
        if exc.field:
            response_kwargs["message"] = f"Validation error for field '{exc.field}'"
        response_kwargs["errors"]["fields"] = error_details

    # Xử lý trường hợp lỗi IntegrityError (trùng lặp, khóa ngoại, ...)
    if isinstance(exc, IntegrityError):
        error_message = str(exc)
        if "duplicate key" in error_message:
            response_kwargs["message"] = "Dữ liệu đã tồn tại trong hệ thống"
        elif "foreign key constraint" in error_message:
            response_kwargs["message"] = "Lỗi ràng buộc khóa ngoại"
        elif "null value" in error_message:
            response_kwargs["message"] = "Dữ liệu không được phép null"
        else:
            response_kwargs["message"] = "Lỗi toàn vẹn dữ liệu"

    # Thêm thông tin request để dễ debug (tùy chọn, có thể loại bỏ trong production)
    if AppMode.DEBUG:
        request_info = None
        if request:
            # Chỉ bao gồm thông tin cần thiết và an toàn
            request_info = {
                "method": request.method,
                "path": request.path,
                "query_params": dict(request.query_params)
                if hasattr(request, "query_params")
                else None,
            }

            # Thêm body data nếu an toàn (không chứa mật khẩu)
            if hasattr(request, "data"):
                data = dict(request.data)
                # Lọc bỏ các thông tin nhạy cảm
                if "password" in data:
                    data["password"] = "***HIDDEN***"
                if "token" in data:
                    data["token"] = "***HIDDEN***"
                request_info["data"] = data

        if response_kwargs["errors"] is None:
            response_kwargs["errors"] = {}

        response_kwargs["errors"]["debug"] = {
            "request": request_info,
            "traceback": _traceback,
        }

    return APIResponse(**response_kwargs)
