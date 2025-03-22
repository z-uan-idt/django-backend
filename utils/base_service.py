from django.apps import apps
from django.db.models import QuerySet, Model, Q
from django.contrib.auth.models import AnonymousUser
from django_currentuser.middleware import get_current_user

from typing import TypeVar, Generic, Optional, Any, Type, List, Literal


T = TypeVar("T", bound=Model)
User = apps.get_model("accounts", "User")
Customer = apps.get_model("accounts", "Customer")


class BaseService(Generic[T]):
    """
    Lớp cơ sở cho tất cả các service trong hệ thống
    Cung cấp các phương thức CRUD cơ bản và truy vấn
    """

    model: Type[T] = None

    def __init__(self, model: Type[T] = None):
        """
        Khởi tạo service với model được chỉ định

        Args:
            model: Lớp model Django
        """
        if model:
            self.model = model
        if self.model is None:
            raise ValueError("Model không được định nghĩa cho service này")
    
    def get_queryset(self):
        return self.model.objects.all()

    def get_objects(
        self,
        keyword: Optional[str] = None,
        prefetch_related: List[Any] = None,
        select_related: List[Any] = None,
        **kwargs,
    ) -> QuerySet[T]:
        """
        Truy vấn đối tượng với các tùy chọn tìm kiếm và lọc

        Args:
            keyword: Từ khóa tìm kiếm
            **kwargs: Các tham số lọc và sắp xếp
                - order_by: Hướng sắp xếp ("asc" hoặc "desc")
                - search_fields: Danh sách các trường cần tìm kiếm
                - Các tham số khác sẽ được sử dụng làm điều kiện lọc

        Returns:
            QuerySet[T]: Danh sách đối tượng phù hợp
        """
        q_filters = Q()

        exclude_kwargs = [
            "order_by",
            "search_fields",
            "page",
            "limit",
            "prefetch_related",
            "select_related",
        ]

        # Xử lý các điều kiện lọc
        for key, value in kwargs.items():
            # Bỏ qua các tham số đặc biệt
            if key in exclude_kwargs:
                continue

            if value is not None:
                q_filters &= Q(**{key: value})

        # Xử lý tìm kiếm theo từ khóa
        if keyword and keyword.strip():
            keyword = keyword.strip()

            search_fields = kwargs.get("search_fields", [])
            if not search_fields:
                raise ValueError("Cần chỉ định search_fields khi sử dụng keyword")

            search_query = Q()
            for field in search_fields:
                search_query |= Q(**{f"{field}__icontains": keyword})

            q_filters &= search_query

        # Thực hiện truy vấn
        objects = self.get_queryset()

        if prefetch_related:
            objects = objects.prefetch_related(*prefetch_related)

        if select_related:
            objects = objects.select_related(*select_related)

        objects = objects.filter(q_filters)

        # Xử lý sắp xếp
        order_by = str(kwargs.get("order_by") or "desc").lower()
        if order_by == "asc":
            objects = objects.order_by("created_at")
        else:
            objects = objects.order_by("-created_at")

        return objects

    def get_by_id(
        self,
        id: Any,
        prefetch_related: List[Any] = None,
        select_related: List[Any] = None,
        **kwargs,
    ) -> T:
        """
        Lấy đối tượng theo ID

        Args:
            id: ID của đối tượng
            **kwargs: Các điều kiện lọc bổ sung

        Returns:
            T: Đối tượng được tìm thấy

        Raises:
            model.DoesNotExist: Nếu không tìm thấy đối tượng
        """
        objects = self.get_queryset()

        if prefetch_related:
            objects = objects.prefetch_related(*prefetch_related)

        if select_related:
            objects = objects.select_related(*select_related)

        return objects.get(pk=id, **kwargs)

    def get_by_filters(
        self,
        prefetch_related: List[Any] = None,
        select_related: List[Any] = None,
        **kwargs,
    ) -> T:
        """
        Lấy đối tượng đầu tiên phù hợp với điều kiện lọc

        Args:
            **kwargs: Các điều kiện lọc

        Returns:
            T: Đối tượng được tìm thấy

        Raises:
            model.DoesNotExist: Nếu không tìm thấy đối tượng
        """
        objects = self.get_queryset()

        if prefetch_related:
            objects = objects.prefetch_related(*prefetch_related)

        if select_related:
            objects = objects.select_related(*select_related)

        return objects.get(**kwargs)

    def exists(self, **kwargs) -> bool:
        """
        Kiểm tra xem đối tượng có tồn tại không

        Args:
            **kwargs: Các điều kiện lọc

        Returns:
            bool: True nếu đối tượng tồn tại, ngược lại False
        """
        return self.get_queryset().filter(**kwargs).exists()

    def create(self, **kwargs) -> T:
        """
        Tạo mới đối tượng

        Args:
            **kwargs: Các tham số cho đối tượng mới

        Returns:
            T: Đối tượng đã được tạo
        """
        instance = self.get_queryset().create(**kwargs)
        return instance

    def update(self, instance: T, **kwargs) -> T:
        """
        Cập nhật đối tượng

        Args:
            instance: Đối tượng cần cập nhật
            **kwargs: Các tham số cần cập nhật

        Returns:
            T: Đối tượng đã được cập nhật
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        """
        Xóa đối tượng

        Args:
            instance: Đối tượng cần xóa
        """
        instance.delete()

    def delete_by_id(self, id: Any) -> None:
        """
        Xóa đối tượng theo ID

        Args:
            id: ID của đối tượng cần xóa

        Raises:
            model.DoesNotExist: Nếu không tìm thấy đối tượng
        """
        instance = self.get_by_id(id)
        self.delete(instance)

    @property
    def current_user(self) -> Optional[Any]:
        """
        Lấy người dùng hiện tại từ request

        Returns:
            Optional[User]: Người dùng SYSTEM: manage
        Returns:
            Optional[Customer]: Người dùng SYSTEM: customer
            Returns:
                None
        """
        return get_current_user()

    @property
    def current_user_system(self) -> Optional[Literal["manage", "customer"]]:
        """
        Lấy loại người dùng hiện tại

        Returns:
            "manage" | "customer" | None
        """
        current_user = self.current_user

        if isinstance(current_user, User):
            return "manage"

        if isinstance(current_user, Customer):
            return "customer"

        return None

    @property
    def is_authenticated(self) -> bool:
        """
        Kiểm tra xem người dùng hiện tại đã xác thực chưa

        Returns:
            bool: True nếu người dùng đã xác thực, ngược lại False
        """
        current_user = self.current_user
        return current_user and not isinstance(current_user, AnonymousUser)
