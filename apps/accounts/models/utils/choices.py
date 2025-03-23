from django.db import models


class GenderChoices(models.TextChoices):
    MALE = 'MALE', 'Nam'
    FEMALE = 'FEMALE', 'Nữ'
    OTHER = 'OTHER', 'Khác'


class UserTypeChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Quản trị viên'
    STAFF = 'STAFF', 'Nhân viên'
    MANAGER = 'MANAGER', 'Quản lý'
    PHARMACY = 'PHARMACY', 'Nhà thuốc'
    SUPPLIER = 'SUPPLIER', 'Nhà cung cấp'
    PARTNER = 'PARTNER', 'Đối tác'
    SELLER = 'SELLER', 'Bán hàng'
    DOCTOR = 'DOCTOR', 'Bác sĩ'
    
    def prefix(type: str):
        return {
            UserTypeChoices.ADMIN: 'QTV',
            UserTypeChoices.STAFF: 'NV',
            UserTypeChoices.MANAGER: 'QL',
            UserTypeChoices.PHARMACY: 'NT',
            UserTypeChoices.SUPPLIER: 'NCC',
            UserTypeChoices.PARTNER: 'DT',
            UserTypeChoices.SELLER: 'BH',
            UserTypeChoices.DOCTOR: 'BS',
        }.get(type)
    
    
class CustomerStatusChoices(models.TextChoices):
    ACTIVATED = 'ACTIVATED', 'Đang hoạt động'
    NOT_ACTIVATED = 'NOT_ACTIVATED', 'Chưa kích hoạt'
    LOCKED = 'LOCKED', 'Vô hiệu hóa'


class UserStatusChoices(models.TextChoices):
    ACTIVATED = 'ACTIVATED', 'Đang hoạt động'
    NOT_ACTIVATED = 'NOT_ACTIVATED', 'Chưa kích hoạt'
    LOCKED = 'LOCKED', 'Vô hiệu hóa'