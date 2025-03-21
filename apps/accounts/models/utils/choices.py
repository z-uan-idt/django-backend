from django.db import models


class GenderChoices(models.TextChoices):
    MALE = 'MALE', 'Nam'
    FEMALE = 'FEMALE', 'Nữ'
    OTHER = 'OTHER', 'Khác'


class UserTypeChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    STAFF = 'STAFF', 'Nhân viên'
    MANAGER = 'MANAGER', 'Quản lý'
    PHARMACY = 'PHARMACY', 'Nhà thuốc'
    SUPPLIER = 'SUPPLIER', 'Nhà cung cấp'
    PARTNER = 'PARTNER', 'Đối tác'
    SELLER = 'SELLER', 'Bán hàng'
    DOCTOR = 'DOCTOR', 'Bác sĩ'
    
    def prefix(type: str):
        return {
            UserTypeChoices.ADMIN: 'AD',
            UserTypeChoices.STAFF: 'ST',
            UserTypeChoices.MANAGER: 'MA',
            UserTypeChoices.PHARMACY: 'PH',
            UserTypeChoices.SUPPLIER: 'SU',
            UserTypeChoices.PARTNER: 'PA',
            UserTypeChoices.SELLER: 'SE',
            UserTypeChoices.DOCTOR: 'DO',
        }.get(type)
    
    
class CustomerStatusChoices(models.TextChoices):
    ACTIVATED = 'ACTIVATED', 'Đang hoạt động'
    NOT_ACTIVATED = 'NOT_ACTIVATED', 'Chưa kích hoạt'
    LOCKED = 'LOCKED', 'Vô hiệu hóa'


class UserStatusChoices(models.TextChoices):
    ACTIVATED = 'ACTIVATED', 'Đang hoạt động'
    NOT_ACTIVATED = 'NOT_ACTIVATED', 'Chưa kích hoạt'
    LOCKED = 'LOCKED', 'Vô hiệu hóa'