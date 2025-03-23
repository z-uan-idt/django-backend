from django.db import models

from constants.error_messages import ErrorMessages

from .utils.phone_user_base import PhoneUserBase
from .utils.choices import UserStatusChoices, UserTypeChoices


class User(PhoneUserBase):
    type = models.CharField(
        verbose_name='Đối tượng',
        error_messages=ErrorMessages.ChoicesField('Đối tượng'),
        choices=UserTypeChoices.choices,
        max_length=100,
        db_index=True,
    )
    status = models.CharField(
        verbose_name='Trạng thái',
        error_messages=ErrorMessages.ChoicesField('Trạng thái'),
        default=UserStatusChoices.ACTIVATED,
        choices=UserStatusChoices.choices,
        max_length=100,
        db_index=True,
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

    class Meta:
        db_table = "accounts_user"
        verbose_name = "Tài khoản người dùng"
        verbose_name_plural = "Tài khoản người dùng"
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_code(prefix=UserTypeChoices.prefix(self.type))
