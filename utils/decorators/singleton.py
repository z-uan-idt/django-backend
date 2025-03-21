from typing import Dict, Type, Callable, TypeVar, Any
import functools


T = TypeVar("T")

_INSTANCES: Dict[Type, Any] = {}


def singleton(cls: Type[T]) -> Callable[..., T]:
    """
    Decorator biến một lớp thành singleton.

    Đảm bảo rằng chỉ có một instance của lớp được tạo ra,
    và các lần gọi tiếp theo sẽ trả về cùng một instance.

    Args:
        cls: Lớp cần biến thành singleton

    Returns:
        Callable: Hàm decorator trả về instance của lớp
    """

    @functools.wraps(cls)
    def decorator(*args, **kwargs) -> T:
        """
        Hàm decorator trả về instance singleton của lớp.

        Args:
            *args: Đối số vị trí cho constructor của lớp
            **kwargs: Đối số từ khóa cho constructor của lớp

        Returns:
            T: Instance singleton của lớp
        """
        if cls not in _INSTANCES:
            _INSTANCES[cls] = cls(*args, **kwargs)

        return _INSTANCES[cls]

    return decorator


def reset_singleton(cls: Type[T]) -> None:
    """
    Xóa instance singleton của một lớp khỏi registry.
    Hữu ích cho việc testing và debugging.

    Args:
        cls: Lớp cần reset singleton
    """
    if cls in _INSTANCES:
        del _INSTANCES[cls]


def get_singleton_instance(cls: Type[T]) -> T:
    """
    Lấy instance singleton của một lớp nếu có.

    Args:
        cls: Lớp cần lấy singleton instance

    Returns:
        T: Instance singleton của lớp hoặc None nếu chưa được khởi tạo

    Raises:
        KeyError: Nếu lớp chưa được khởi tạo
    """
    if cls not in _INSTANCES:
        raise KeyError(f"Singleton instance of {cls.__name__} not initialized")

    return _INSTANCES[cls]


def has_singleton_instance(cls: Type[T]) -> bool:
    """
    Kiểm tra xem một lớp đã có singleton instance chưa.

    Args:
        cls: Lớp cần kiểm tra

    Returns:
        bool: True nếu lớp đã có singleton instance, False nếu chưa
    """
    return cls in _INSTANCES
