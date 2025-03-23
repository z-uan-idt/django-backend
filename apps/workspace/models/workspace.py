from django.db import models

from utils.base_models import BaseModelSoftDelete
from constants.error_messages import ErrorMessages


class Workspace(BaseModelSoftDelete):
    name = models.CharField(
        verbose_name='Tên workspace',
        error_messages=ErrorMessages.CharField('Tên workspace', 255),
        max_length=255,
        db_index=True,
    )
    code = models.CharField(
        verbose_name='Mã workspace',
        error_messages=ErrorMessages.CharField('Mã workspace', 100),
        max_length=100,
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Mô tả',
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='Workspace cha',
        related_name='workspace_parent',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        to='accounts.User',
        verbose_name='Chủ workspace',
        related_name='workspace_owner',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    users = models.ManyToManyField(
        to='accounts.User',
        through='workspace.WorkspaceUser',
        related_name='workspace_users',
        verbose_name='Người dùng',
        blank=True,
    )
    customers = models.ManyToManyField(
        to='accounts.Customer',
        through='workspace.WorkspaceCustomer',
        related_name='workspace_customers',
        verbose_name='Khách hàng',
        blank=True,
    )
    created_by = models.ForeignKey(
        to='accounts.User',
        verbose_name='Người tạo',
        on_delete=models.SET_NULL,
        related_name='created_workspace',
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        to='accounts.User',
        verbose_name='Người cập nhật',
        on_delete=models.SET_NULL,
        related_name='updated_workspace',  
        blank=True,
        null=True,
    )

    class Meta:
        db_table = 'workspace_workspace'
        verbose_name_plural = 'Workspace'
        verbose_name = 'Workspace'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                condition=models.Q(is_delete=False),
                name='unique_workspace_code',
                fields=['code'],
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class WorkspaceMemberBase(models.Model):
    workspace = models.ForeignKey(
        Workspace,
        verbose_name='Workspace',
        on_delete=models.CASCADE
    )
    joined_at = models.DateTimeField(
        verbose_name='Ngày tham gia',
        auto_now_add=True
    )
    left_at = models.DateTimeField(
        verbose_name='Ngày rời khỏi workspace',
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
        ordering = ['-joined_at']


class WorkspaceUser(WorkspaceMemberBase):
    user = models.ForeignKey(
        to='accounts.User',
        verbose_name='Người dùng',
        on_delete=models.CASCADE,
        related_name='workspace_user_user'
    )
    positions = models.ManyToManyField(
        'workspace.Position',
        verbose_name='Chức vụ',
        related_name='workspace_user_positions',
        blank=True,
    )

    class Meta:
        db_table = 'workspace_user'
        verbose_name = 'Người dùng trong workspace'
        verbose_name_plural = 'Người dùng trong workspace'
        unique_together = [['workspace', 'user']]

    def __str__(self):
        return f"{self.user.full_name} - {self.workspace.name}"


class WorkspaceCustomer(WorkspaceMemberBase):
    customer = models.ForeignKey(
        to='accounts.Customer',
        verbose_name='Khách hàng',
        on_delete=models.CASCADE,
        related_name='workspace_customer_customer'
    )
    positions = models.ManyToManyField(
        'workspace.Position',
        verbose_name='Chức vụ',
        related_name='workspace_customer_positions',
        blank=True,
    )

    class Meta:
        db_table = 'workspace_customer'
        verbose_name = 'Khách hàng trong workspace'
        verbose_name_plural = 'Khách hàng trong workspace'
        unique_together = [['workspace', 'customer']]

    def __str__(self):
        return f"{self.customer.full_name} - {self.workspace.name}" 