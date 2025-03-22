from django.contrib.auth.models import AbstractUser
from django.db import models

from constants.error_messages import ErrorMessages

from .utils.manager import AdminUserManager


class AdminUser(AbstractUser):
    username = models.CharField(
        error_messages=ErrorMessages.CharField("Tài khoản", 150),
        verbose_name="Tài khoản",
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        error_messages=ErrorMessages.CharField("Mật khẩu", 128),
        verbose_name="Mật khẩu",
        max_length=128,
    )
    full_name = models.CharField(
        error_messages=ErrorMessages.CharField("Họ và Tên", 255),
        verbose_name="Họ và Tên",
        max_length=255,
    )

    # Loại bỏ
    EMAIL_FIELD, user_permissions, groups = None, None, None
    email, last_name, first_name = None, None, None
    last_login, date_joined = None, None

    # Mặc định
    is_staff, is_active, is_superuser = True, True, True

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    objects = AdminUserManager()

    class Meta:
        db_table = "accounts_admin_user"
        verbose_name = "Tài khoản quản trị hệ thống"
        verbose_name_plural = "Tài khoản quản trị hệ thống"
        ordering = ["-id"]

    def __str__(self):
        return "{}: {} {}".format(self.pk, self.username, self.full_name)
