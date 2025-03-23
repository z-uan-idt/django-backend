from django.db import models

from django_currentuser.middleware import get_current_user

from constants.error_messages import ErrorMessages

from .utils.phone_user_base import PhoneUserBase
from .utils.choices import CustomerStatusChoices


class Customer(PhoneUserBase):
    status = models.CharField(
        error_messages=ErrorMessages.ChoicesField('Trạng thái'),
        default=CustomerStatusChoices.ACTIVATED,
        choices=CustomerStatusChoices.choices,
        verbose_name='Trạng thái',
        max_length=100,
        db_index=True,
    )
    representative = models.ForeignKey(
        null=True,
        blank=True,
        to="accounts.User",
        on_delete=models.SET_NULL,
        verbose_name='Người đại diện',
        related_name="customer_representative",
    )

    class Meta:
        db_table = "accounts_customer"
        verbose_name = "Tài khoản khách hàng"
        verbose_name_plural = "Tài khoản khách hàng"
        constraints = [
            models.UniqueConstraint(
                condition=models.Q(is_delete=False) & ~models.Q(phone_number__isnull=True) & ~models.Q(phone_number__exact=''),
                name='unique_active_customer_phone_number',
                fields=['phone_number'],
            ),
            models.UniqueConstraint(
                condition=models.Q(is_delete=False) & ~models.Q(code__isnull=True) & ~models.Q(code__exact=''),
                name='unique_customer_code',
                fields=['code'],
            ),
        ]

    def __str__(self):
        return "{}: {} - {}".format(self.pk, self.full_name, self.phone_number)

    def save(self, *args, **kwargs):
        if not self.pk and not self.representative:
            current_user = get_current_user()
            if self.get_related_model('representative', current_user):
                self.representative = current_user
        
        super().save(*args, **kwargs)

        self.generate_code(prefix="KH")
