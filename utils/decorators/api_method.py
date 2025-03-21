from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema

from typing import List, Optional, Callable

from utils.decorators import singleton


@singleton
class APIMethod:
    """
    Singleton cung cấp các phương thức tiện ích để đăng ký API endpoints
    """

    def registry(
        self,
        method: str,
        url_path: Optional[str] = None,
        detail: bool = False,
        parsers: Optional[List] = None,
        permission_classes: Optional[List] = None,
        authentication_classes: Optional[List] = None,
        **kwargs
    ) -> Callable:
        """
        Đăng ký một API endpoint

        Args:
            method: HTTP method (get, post, put, patch, delete)
            url_path: Đường dẫn URL
            detail: True nếu endpoint là detail view
            parsers: Danh sách parser classes
            permission_classes: Danh sách permission classes
            authentication_classes: Danh sách authentication classes
            **kwargs: Tham số bổ sung cho @action decorator

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """

        # Thêm các tham số vào kwargs nếu được cung cấp
        if authentication_classes is not None:
            kwargs["authentication_classes"] = authentication_classes
        if permission_classes is not None:
            kwargs["permission_classes"] = permission_classes
        if parsers:
            kwargs["parser_classes"] = parsers

        # Sử dụng DRF action decorator
        return action(
            detail=detail,
            methods=[method],
            url_path=url_path,
            **kwargs,
        )

    def post(
        self,
        url_path: Optional[str] = None,
        authentication_classes: Optional[List] = None,
        permission_classes: Optional[List] = None,
        parsers: Optional[List] = None,
        **kwargs
    ) -> Callable:
        """
        Đăng ký một POST endpoint

        Args:
            url_path: Đường dẫn URL
            authentication_classes: Danh sách authentication classes
            permission_classes: Danh sách permission classes
            parsers: Danh sách parser classes
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            detail=False,
            method="post",
            parsers=parsers,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def put(
        self,
        url_path: Optional[str] = None,
        authentication_classes: Optional[List] = None,
        permission_classes: Optional[List] = None,
        parsers: Optional[List] = None,
        **kwargs
    ) -> Callable:
        """
        Đăng ký một PUT endpoint

        Args:
            url_path: Đường dẫn URL
            authentication_classes: Danh sách authentication classes
            permission_classes: Danh sách permission classes
            parsers: Danh sách parser classes
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            detail=True,
            method="put",
            parsers=parsers,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def get(
        self,
        url_path: Optional[str] = None,
        detail: bool = False,
        authentication_classes: Optional[List] = None,
        permission_classes: Optional[List] = None,
        **kwargs
    ) -> Callable:
        """
        Đăng ký một GET endpoint

        Args:
            url_path: Đường dẫn URL
            detail: True nếu endpoint là detail view
            authentication_classes: Danh sách authentication classes
            permission_classes: Danh sách permission classes
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            parsers=None,
            method="get",
            detail=detail,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def delete(
        self,
        url_path: Optional[str] = None,
        permission_classes: Optional[List] = None,
        authentication_classes: Optional[List] = None,
        **kwargs
    ) -> Callable:
        """
        Đăng ký một DELETE endpoint

        Args:
            url_path: Đường dẫn URL
            permission_classes: Danh sách permission classes
            authentication_classes: Danh sách authentication classes
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            detail=True,
            parsers=None,
            method="delete",
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def patch(
        self,
        url_path: Optional[str] = None,
        parsers: Optional[List] = None,
        permission_classes: Optional[List] = None,
        authentication_classes: Optional[List] = None,
        **kwargs
    ) -> Callable:
        """
        Đăng ký một PATCH endpoint

        Args:
            url_path: Đường dẫn URL
            parsers: Danh sách parser classes
            permission_classes: Danh sách permission classes
            authentication_classes: Danh sách authentication classes
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            detail=True,
            method="patch",
            parsers=parsers,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def options(
        self, url_path: Optional[str] = None, detail: bool = False, **kwargs
    ) -> Callable:
        """
        Đăng ký một OPTIONS endpoint

        Args:
            url_path: Đường dẫn URL
            detail: True nếu endpoint là detail view
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            method="options",
            detail=detail,
            url_path=url_path,
            **kwargs,
        )

    def head(
        self, url_path: Optional[str] = None, detail: bool = False, **kwargs
    ) -> Callable:
        """
        Đăng ký một HEAD endpoint

        Args:
            url_path: Đường dẫn URL
            detail: True nếu endpoint là detail view
            **kwargs: Tham số bổ sung

        Returns:
            Callable: Decorator có thể áp dụng cho view method
        """
        return self.registry(
            method="head",
            detail=detail,
            url_path=url_path,
            **kwargs,
        )

    @property
    def swagger(self):
        """
        Trả về swagger_auto_schema để sử dụng trong API documentation

        Returns:
            Callable: swagger_auto_schema decorator
        """
        return swagger_auto_schema


# Khởi tạo singleton instance
api = APIMethod()
