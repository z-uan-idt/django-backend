from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from datetime import datetime

from utils.base_models import BaseModelSoftDelete
from constants.error_messages import ErrorMessages

from .validators import validate_phone_number
from .choices import GenderChoices


class PhoneUserBase(AbstractBaseUser, BaseModelSoftDelete):
    phone_number = models.CharField(
        error_messages=ErrorMessages.CharField('Số điện thoại', 128),
        validators=[validate_phone_number],
        verbose_name='Số điện thoại',
        max_length=128,
        unique=True,
        db_index=True,
    )
    password = models.CharField(
        error_messages=ErrorMessages.CharField('Mật khẩu', 128),
        verbose_name='Mật khẩu',
        max_length=128,
    )
    code = models.CharField(
        error_messages=ErrorMessages.CharField('Mã', 100),
        verbose_name='Mã',
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    
    # Common Information
    full_name = models.CharField(
        error_messages=ErrorMessages.CharField('Họ và Tên', 255),
        verbose_name='Họ và Tên',
        max_length=255,
        db_index=True,
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
        db_index=True,
    )
    date_of_birth = models.DateField(
        error_messages=ErrorMessages.DateField('Ngày sinh'),
        verbose_name='Ngày sinh',
        blank=True,
        null=True,
    )

    REQUIRED_FIELDS = ["full_name"]
    USERNAME_FIELD = "phone_number"
    
    last_login = None

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["full_name"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["email"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return "{}: {} - {}".format(self.pk, self.full_name, self.phone_number)

    def generate_code(self, prefix, digit_length=5, commit=True):
        if self.pk and not self.code:
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

    def delete(self, using=None, keep_parents=False, hard_delete=False):
        return super().delete(using, keep_parents, hard_delete, delete_keys=["phone_number"]) 