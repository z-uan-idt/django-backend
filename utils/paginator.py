from django.utils.functional import cached_property
from django.utils.inspect import method_has_no_args
from django.db.models.query import QuerySet

from rest_framework.request import Request

from typing import Union, List, Dict, Any, Optional, Callable, TypeVar, Generic

import inspect
import math

from utils.exception import MessageError


T = TypeVar("T")
R = TypeVar("R")


class Paginator(Generic[T]):
    """
    Lớp Paginator để chia collection thành các trang với chức năng nâng cao.

    Lớp này xử lý phân trang cho cả Django QuerySets và danh sách Python thông thường,
    hỗ trợ serialization và định dạng tùy chỉnh cho kết quả.
    """

    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MIN_PAGE = 1  # Trang tối thiểu
    MAX_PER_PAGE = 100  # Ngăn chặn kích thước truy vấn quá lớn

    def __init__(self, object_list: Union[List[T], QuerySet], per_page: int = 10):
        """
        Khởi tạo một instance Paginator mới.

        Tham số:
            object_list: Danh sách hoặc queryset để phân trang
            per_page: Số lượng mục trên mỗi trang (mặc định: 10)

        Raises:
            ValueError: Nếu per_page nhỏ hơn 1
        """
        if per_page < 1:
            raise ValueError("per_page phải ít nhất là 1")

        if per_page > self.MAX_PER_PAGE:
            per_page = self.MAX_PER_PAGE

        self._object_list = object_list
        self.per_page = per_page
        self.current_page = 1
        self.bottom = 0
        self.top = 0
        self.classes: Optional[Callable] = None
        self.option_classes: Dict[str, Any] = {}

    @staticmethod
    def from_request(request: Request, key: str = "page") -> int:
        """
        Trích xuất tham số phân trang từ request.

        Tham số:
            request: Đối tượng Request của DRF
            key: Tên tham số để trích xuất (ví dụ: "page" hoặc "limit")

        Trả về:
            int: Giá trị được trích xuất, hoặc giá trị mặc định nếu không có

        Raises:
            ValueError: Nếu tham số tồn tại nhưng không phải là số nguyên
        """
        # Thử lấy giá trị từ query params hoặc dữ liệu request
        page_value = request.query_params.get(key)

        if page_value is None and hasattr(request, "data"):
            try:
                page_value = request.data.get(key)
            except (AttributeError, TypeError):
                page_value = None

        # Đặt giá trị mặc định dựa trên key
        if not page_value:
            if key == "page":
                page_value = Paginator.DEFAULT_PAGE
            elif key == "limit":
                page_value = Paginator.DEFAULT_PER_PAGE

        # Chuyển đổi thành số nguyên
        try:
            return int(page_value)
        except (ValueError, TypeError):
            if key == "page":
                return Paginator.DEFAULT_PAGE
            elif key == "limit":
                return Paginator.DEFAULT_PER_PAGE
            return 0

    def page(self, page_number: int = 1) -> "Paginator[T]":
        """
        Lấy một trang cụ thể.

        Tham số:
            page_number: Số trang (bắt đầu từ 1)

        Trả về:
            Paginator: Self, để có thể gọi phương thức theo chuỗi

        Raises:
            ValueError: Nếu page_number nhỏ hơn 1 hoặc lớn hơn tổng số trang
        """
        if not isinstance(page_number, int):
            try:
                page_number = int(page_number)
            except (ValueError, TypeError):
                page_number = 1

        if page_number < 1:
            page_number = 1

        self.current_page = page_number
        current_page_index = page_number - 1

        # Tính toán giới hạn cắt (slice)
        self.bottom = current_page_index * self.per_page
        self.top = min(self.per_page + self.bottom, self.count)

        # Kiểm tra nếu trang tồn tại
        if page_number > self.num_pages and self.num_pages > 0:
            message = f"Trang {page_number} vượt quá số trang tối đa {self.num_pages}"
            raise MessageError(message)

        return self

    def set_results_classes(
        self, classes: Callable[[List[T]], Any], option: Dict[str, Any] = {}
    ) -> "Paginator[T]":
        """
        Đặt lớp serializer để sử dụng cho kết quả.

        Tham số:
            classes: Lớp serializer hoặc hàm
            option: Tùy chọn bổ sung để truyền vào serializer

        Trả về:
            Paginator: Self, để có thể gọi phương thức theo chuỗi
        """
        self.option_classes = option
        self.classes = classes
        return self

    @cached_property
    def num_pages(self) -> int:
        """
        Tính tổng số trang.

        Trả về:
            int: Tổng số trang
        """
        if self.count == 0:
            return 0
        return math.ceil(self.count / self.per_page)

    @cached_property
    def count(self) -> int:
        """
        Lấy tổng số mục.

        Cố gắng sử dụng phương thức count() của đối tượng nếu có, nếu không sẽ sử dụng len().

        Trả về:
            int: Tổng số mục
        """
        try:
            # Thử sử dụng phương thức count() cho QuerySets (hiệu quả hơn)
            count_method = getattr(self._object_list, "count", None)
            if (
                callable(count_method)
                and not inspect.isbuiltin(count_method)
                and method_has_no_args(count_method)
            ):
                return count_method()

            # Sử dụng len cho danh sách thông thường
            return len(self._object_list)
        except (TypeError, AttributeError) as e:
            return 0

    @cached_property
    def object_results(self) -> List[T]:
        """
        Lấy các đối tượng cho trang hiện tại.

        Trả về:
            List: Các đối tượng cho trang hiện tại
        """
        try:
            # Xử lý cả danh sách và queryset
            if isinstance(self._object_list, QuerySet):
                # Đối với QuerySets, việc cắt tạo ra một truy vấn SQL LIMIT/OFFSET hiệu quả
                return list(self._object_list[self.bottom : self.top])
            else:
                # Đối với danh sách, chỉ cắt như bình thường
                return self._object_list[self.bottom : self.top]
        except Exception as e:
            return []

    @cached_property
    def results(self) -> Any:
        """
        Lấy kết quả đã được serialized cho trang hiện tại.

        Nếu lớp serializer được đặt, nó sẽ được sử dụng để serialize các đối tượng.
        Nếu không, các đối tượng gốc sẽ được trả về.

        Trả về:
            Any: Kết quả đã được serialized
        """
        try:
            if not self.object_results:
                return []

            # Nếu có cung cấp lớp serializer, sử dụng nó
            if hasattr(self, "classes") and self.classes is not None:
                kwargs = {"many": True}
                if hasattr(self, "option_classes"):
                    kwargs.update(self.option_classes)
                return self.classes(self.object_results, **kwargs).data

            # Nếu đối tượng có phương thức values (như QuerySets), sử dụng nó
            if hasattr(self.object_results, "values"):
                return list(self.object_results.values())

            # Nếu không thì trả về trực tiếp các đối tượng
            return self.object_results
        except Exception as e:
            return []

    @cached_property
    def output_results(self) -> Dict[str, Any]:
        """
        Lấy một từ điển chứa metadata phân trang và kết quả.

        Trả về:
            Dict: Thông tin phân trang và kết quả
        """
        return {
            "count": self.count,
            "num_pages": self.num_pages,
            "current_page": self.current_page,
            "previous_page": self.previous_page,
            "next_page": self.next_page,
            "per_page": self.per_page,
            "results": self.results,
        }

    def get_output_results(self, results: List[Any]) -> Dict[str, Any]:
        """
        Lấy một từ điển chứa metadata phân trang và kết quả tùy chỉnh.

        Điều này cho phép cung cấp kết quả tùy chỉnh thay vì sử dụng kết quả đã được serialized mặc định.

        Tham số:
            results: Kết quả tùy chỉnh để bao gồm

        Trả về:
            Dict: Thông tin phân trang và kết quả tùy chỉnh
        """
        return {
            "count": self.count,
            "num_pages": self.num_pages,
            "current_page": self.current_page,
            "previous_page": self.previous_page,
            "next_page": self.next_page,
            "per_page": self.per_page,
            "results": results,
        }

    @cached_property
    def previous_page(self) -> Optional[int]:
        """
        Lấy số trang trước đó hoặc None nếu đang ở trang đầu tiên.

        Trả về:
            Optional[int]: Số trang trước đó hoặc None
        """
        return self.current_page - 1 if self.current_page > 1 else None

    @cached_property
    def next_page(self) -> Optional[int]:
        """
        Lấy số trang tiếp theo hoặc None nếu đang ở trang cuối cùng.

        Trả về:
            Optional[int]: Số trang tiếp theo hoặc None
        """
        return self.current_page + 1 if self.current_page < self.num_pages else None

    def has_next(self) -> bool:
        """
        Kiểm tra xem có trang tiếp theo hay không.

        Trả về:
            bool: True nếu có trang tiếp theo
        """
        return self.current_page < self.num_pages

    def has_previous(self) -> bool:
        """
        Kiểm tra xem có trang trước đó hay không.

        Trả về:
            bool: True nếu có trang trước đó
        """
        return self.current_page > 1
