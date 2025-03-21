from django.db import models
from django.db.models.query import QuerySet

from typing import Any, Optional, TypeVar


T = TypeVar("T")


class PostgresqlJsonField(models.JSONField):
    """
    Trường JSON tùy chỉnh cho PostgreSQL để xử lý dữ liệu JSON.

    Lớp này mở rộng JSONField mặc định của Django để đảm bảo xử lý đúng
    giá trị từ cơ sở dữ liệu PostgreSQL.
    """

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> Any:
        """
        Xử lý giá trị JSON khi lấy từ cơ sở dữ liệu.

        Args:
            value: Giá trị JSON từ cơ sở dữ liệu
            expression: Biểu thức truy vấn
            connection: Kết nối cơ sở dữ liệu

        Returns:
            Any: Giá trị JSON đã được xử lý
        """
        # Trả về trực tiếp giá trị, PostgreSQL đã xử lý JSON đúng cách
        return value

    def get_prep_value(self, value: Any) -> Any:
        """
        Chuẩn bị giá trị để lưu vào cơ sở dữ liệu.

        Args:
            value: Giá trị cần chuẩn bị

        Returns:
            Any: Giá trị đã chuẩn bị
        """
        # Sử dụng phương thức của lớp cha
        return super().get_prep_value(value)


class SubqueryJson(models.Subquery):
    """
    Lớp Subquery để chuyển đổi kết quả truy vấn con thành đối tượng JSON.

    Sử dụng PostgreSQL row_to_json để chuyển đổi một hàng kết quả thành đối tượng JSON.
    """

    template = "(SELECT row_to_json(_subquery) FROM (%(subquery)s) _subquery)"
    output_field = PostgresqlJsonField()

    def __init__(self, queryset: QuerySet, **kwargs: Any) -> None:
        """
        Khởi tạo một đối tượng SubqueryJson.

        Args:
            queryset: Truy vấn con để chuyển đổi thành JSON
            **kwargs: Đối số từ khóa bổ sung
        """
        try:
            super().__init__(queryset, **kwargs)
        except Exception as e:
            print(f"Lỗi khi khởi tạo SubqueryJson: {e}")
            raise


class SubqueryJsonAgg(models.Subquery):
    """
    Lớp Subquery để tổng hợp các kết quả truy vấn con thành một mảng JSON.

    Sử dụng PostgreSQL array_to_json và array_agg để chuyển đổi nhiều hàng
    thành một mảng JSON. Hỗ trợ cả giá trị phẳng và đối tượng.

    Options:
        - return_none: Nếu True, trả về None thay vì mảng rỗng khi không có kết quả
    """

    # Template mặc định cho trường hợp trả về mảng rỗng
    template = "(SELECT array_to_json(coalesce(array_agg(row_to_json(_subquery)), array[]::json[])) FROM (%(subquery)s) _subquery)"
    # Template cho trường hợp trả về NULL
    template_return_none = "(SELECT CASE WHEN COUNT(*) = 0 THEN NULL ELSE array_to_json(array_agg(row_to_json(_subquery))) END FROM (%(subquery)s) _subquery)"

    output_field = PostgresqlJsonField()

    def __init__(
        self,
        queryset: QuerySet,
        alias: Optional[str] = None,
        flat: bool = False,
        return_none: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Khởi tạo một đối tượng SubqueryJsonAgg.

        Args:
            queryset: Truy vấn con để tổng hợp thành mảng JSON
            alias: Tên trường để sử dụng khi flat=True
            flat: Nếu True, sẽ tổng hợp chỉ một cột thay vì toàn bộ hàng
            return_none: Nếu True, trả về None thay vì mảng rỗng khi không có kết quả
            **kwargs: Đối số từ khóa bổ sung
        """
        self.flat = flat
        self.return_none = return_none

        try:
            # Nếu flat=True, chỉ lấy giá trị của cột được chỉ định bởi alias
            if self.flat:
                if not alias:
                    raise ValueError("Khi flat=True, alias không được để trống")
                queryset = queryset.values_list(alias, flat=True)

            # Khởi tạo lớp cha
            super().__init__(queryset, **kwargs)
        except Exception as e:
            raise

    def as_sql(
        self, compiler: Any, connection: Any, template: Optional[str] = None
    ) -> tuple:
        """
        Tạo câu lệnh SQL cho subquery này.

        Args:
            compiler: Trình biên dịch SQL Django
            connection: Kết nối cơ sở dữ liệu
            template: Mẫu SQL tùy chỉnh (tùy chọn)

        Returns:
            tuple: Tuple chứa câu lệnh SQL và các tham số
        """
        try:
            # Xác định giá trị để tổng hợp dựa trên cấu hình flat
            if self.flat:
                # Nếu flat=True, chỉ lấy giá trị của cột đầu tiên
                if (
                    hasattr(self.queryset, "query")
                    and hasattr(self.queryset.query, "values")
                    and self.queryset.query.values
                ):
                    self.extra["value"] = f"_subquery.{self.queryset.query.values[0]}"
                else:
                    raise ValueError("Không tìm thấy giá trị để tổng hợp")
            else:
                # Nếu flat=False, chuyển đổi toàn bộ hàng thành JSON
                self.extra["value"] = "row_to_json(_subquery)"

            # Sử dụng template thích hợp dựa trên tùy chọn return_none
            selected_template = (
                self.template_return_none
                if self.return_none
                else template or self.template
            )

            return super().as_sql(compiler, connection, selected_template)
        except Exception as e:
            raise


class UnaccentVN(models.Func):
    """
    Hàm để loại bỏ dấu trong tiếng Việt.

    Sử dụng hàm 'translate' của PostgreSQL để thay thế các ký tự có dấu
    bằng các ký tự không dấu tương ứng.
    """

    function = "unaccent_vn"
    template = "translate(%(expressions)s, 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựíìỉĩịýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴĐ', 'aaaaaaaaaaaaaaaaaeeeeeeeeeeeooooooooooooooooouuuuuuuuuuuiiiiiyyyyydAAAAAAAAAAAAAAAAAEEEEEEEEEEEOOOOOOOOOOOOOOOOOUUUUUUUUUUUIIIIIYYYYYD')"
    output_field = models.CharField()

    def __init__(self, expression: Any, **extra: Any) -> None:
        """
        Khởi tạo hàm UnaccentVN.

        Args:
            expression: Biểu thức cần loại bỏ dấu
            **extra: Tham số bổ sung
        """
        try:
            super().__init__(expression, **extra)
        except Exception as e:
            print(f"Lỗi khi khởi tạo UnaccentVN: {e}")
            raise


# Các hàm tiện ích bổ sung
def json_build_object(**kwargs: Any) -> models.Func:
    """
    Tạo một đối tượng JSON từ các cặp khóa-giá trị.

    Args:
        **kwargs: Các cặp khóa-giá trị để đưa vào đối tượng JSON

    Returns:
        models.Func: Biểu thức SQL để tạo đối tượng JSON
    """
    args = []
    for key, value in kwargs.items():
        args.extend([models.Value(key), value])

    return models.Func(
        *args, function="json_build_object", output_field=PostgresqlJsonField()
    )


def json_agg(expression: Any) -> models.Func:
    """
    Tổng hợp các giá trị thành một mảng JSON.

    Args:
        expression: Biểu thức cần tổng hợp

    Returns:
        models.Func: Biểu thức SQL để tổng hợp thành mảng JSON
    """
    return models.Func(
        expression, function="json_agg", output_field=PostgresqlJsonField()
    )


def lower_unaccent(expression: Any) -> models.Func:
    """
    Chuyển đổi biểu thức thành chữ thường và loại bỏ dấu.

    Args:
        expression: Biểu thức cần xử lý

    Returns:
        models.Func: Biểu thức SQL đã được xử lý
    """
    return models.Func(
        UnaccentVN(models.functions.Lower(expression)),
        function="TRIM",
        output_field=models.CharField(),
    )
