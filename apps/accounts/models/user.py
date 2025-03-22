from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from datetime import datetime

from utils.base_models import BaseModelSoftDelete
from constants.error_messages import ErrorMessages

from .utils.choices import UserStatusChoices, GenderChoices, UserTypeChoices
from .utils.validators import validate_phone_number


class User(AbstractBaseUser, BaseModelSoftDelete):
    phone_number = models.CharField(
        error_messages=ErrorMessages.CharField('Số điện thoại', 128),
        validators=[validate_phone_number],
        verbose_name='Số điện thoại',
        max_length=128,
        unique=True,
    )
    password = models.CharField(
        error_messages=ErrorMessages.CharField('Mật khẩu', 128),
        verbose_name='Mật khẩu',
        max_length=128,
    )
    code = models.CharField(
        error_messages=ErrorMessages.CharField('Mã người dùng', 100),
        verbose_name='Mã người dùng',
        max_length=100,
        blank=True,
        null=True,
    )
    
    # Thông tin người dùng
    full_name = models.CharField(
        error_messages=ErrorMessages.CharField('Tên người dùng', 255),
        verbose_name='Tên người dùng',
        max_length=255,
    )
    gender = models.CharField(
        error_messages=ErrorMessages.ChoicesField('Giới tính'),
        choices=GenderChoices.choices,
        verbose_name='Giới tính',
        max_length=20,
        blank=True,
        null=True
    )
    email = models.EmailField(
        error_messages=ErrorMessages.CharField('Địa chỉ email', 255),
        verbose_name='Địa chỉ email',
        max_length=255,
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        error_messages=ErrorMessages.DateField('Ngày sinh'),
        verbose_name='Ngày sinh',
        blank=True,
        null=True,
    )
    
    # Thông tin chung
    type = models.CharField(
        error_messages=ErrorMessages.ChoicesField('Đối tượng người dùng'),
        verbose_name='Đối tượng người dùng',
        choices=UserTypeChoices.choices,
        max_length=100,
    )
    status = models.CharField(
        error_messages=ErrorMessages.ChoicesField('Trạng thái người dùng'),
        verbose_name='Trạng thái người dùng',
        default=UserStatusChoices.ACTIVATED,
        choices=UserStatusChoices.choices,
        max_length=100,
    )
    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name='Người tạo',
        on_delete=models.SET_NULL,
        related_name="user_created_by",
    )
    updated_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Người cập nhật',
        related_name="user_updated_by",
    )
    deleted_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name='Người xóa',
        on_delete=models.SET_NULL,
        related_name="user_deleted_by",
    )

    REQUIRED_FIELDS = ["full_name"]
    USERNAME_FIELD = "phone_number"
    
    last_login = None

    class Meta:
        db_table = "accounts_user"
        verbose_name = "Tài khoản người dùng"
        verbose_name_plural = "Tài khoản người dùng"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["full_name"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["phone_number"]),
        ]
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                condition=models.Q(is_delete=False) & ~models.Q(phone_number__isnull=True) & ~models.Q(phone_number__exact=''),
                name='unique_active_user_phone_number',
                fields=['phone_number'],
            ),
            models.UniqueConstraint(
                condition=models.Q(is_delete=False) & ~models.Q(code__isnull=True) & ~models.Q(code__exact=''),
                name='unique_user_code',
                fields=['code'],
            ),
        ]

    def __str__(self):
        return "{}: {} - {}".format(self.pk, self.full_name, self.phone_number)
    
    def generate_code(self, digit_length=5, commit=True):
        if self.pk and not self.code:
            prefix = UserTypeChoices.prefix(self.type)
            date_str = datetime.now().strftime("%Y%m%d")
            random_digits = str(self.pk).zfill(digit_length)
            self.code = f"{prefix}{date_str}{random_digits}"
            if commit:
                self.save(update_fields=["code"])
        
        return self.code

    def save(self, *args, **kwargs):
        if self.pk:
            deleted_flag = f"__deleted__{self.pk}"

            if self.is_delete and self.phone_number and not self.phone_number.endswith(deleted_flag):
                self.phone_number = f"{self.phone_number}{deleted_flag}"
        
        super().save(*args, **kwargs)
        
        self.generate_code()

    def delete(self, using=None, keep_parents=False, hard_delete=False):
        return super().delete(using, keep_parents, hard_delete, delete_keys=["phone_number"])
