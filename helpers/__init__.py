from decimal import Decimal

import math
import re


def is_empty(value) -> bool:
    if value is None:
        return True

    if isinstance(value, (list, tuple, str, dict, set)):
        return len(value) == 0

    return False


def bigger(value, n=0):
    return len(value) > n


def equal(value, n=0):
    return len(value) == n


def smaller(value, n=0):
    return len(value) < n


def compare_versions(old_version, new_version):
    if not old_version:
        old_version = "0.0.0"

    if not new_version:
        new_version = "0.0.0"

    old_parts = list(map(int, old_version.split(".")))
    new_parts = list(map(int, new_version.split(".")))

    for old, new in zip(old_parts, new_parts):
        if new > old:
            return True
        elif new < old:
            return False

    return len(new_parts) > len(old_parts)


def is_integer(value):
    if isinstance(value, int):
        return True

    if isinstance(value, float):
        if value.is_integer():
            return True
        return False

    if isinstance(value, Decimal):
        return value % 1 == 0

    if isinstance(value, str):
        try:
            int(value)
            return True
        except ValueError:
            try:
                return float(value).is_integer()
            except ValueError:
                return False

    return False


def is_float(value):
    if isinstance(value, float):
        return True

    if isinstance(value, Decimal):
        return value % 1 != 0

    if isinstance(value, str):
        try:
            int(value)
            return False
        except ValueError:
            try:
                float(value)
                return True
            except ValueError:
                return False

    if isinstance(value, int):
        return False

    return False


def get_number_type(value):
    if is_integer(value):
        return "integer"
    elif is_float(value):
        return "float"

    return "not_a_number"


def has_phone_number(phone_number):
    return re.match(
        r"^0{10}$|(03[2-9]|05[6-8]|07[0-9]|08[1-5]|09[0-9])[0-9]{7}$", phone_number
    )


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "-")
    return ip


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách Haversine giữa hai điểm dựa trên tọa độ địa lý.

    Args:
        lat1: Vĩ độ của điểm thứ nhất
        lon1: Kinh độ của điểm thứ nhất
        lat2: Vĩ độ của điểm thứ hai
        lon2: Kinh độ của điểm thứ hai

    Returns:
        Khoảng cách giữa hai điểm tính bằng km
    """
    # Chuyển đổi độ sang radian
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Công thức Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Bán kính Trái Đất (km)

    return c * r
