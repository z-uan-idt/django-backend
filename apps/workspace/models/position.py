from django.db import models

from constants.error_messages import ErrorMessages


class Position(models.Model):
    name = models.CharField(
        verbose_name='Tên chức vụ',
        error_messages=ErrorMessages.CharField('Tên chức vụ', 255),
        max_length=255,
        db_index=True,
    )
    code = models.CharField(
        verbose_name='Mã chức vụ',
        error_messages=ErrorMessages.CharField('Mã chức vụ', 100),
        max_length=100,
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Mô tả',
        blank=True,
        null=True,
    )
    actions = models.ManyToManyField(
        to='workspace.Action',
        verbose_name='Hành động',
        related_name='position_actions',
        blank=True,
    )
    is_default = models.BooleanField(
        verbose_name='Mặc định',
        default=True
    )
    workspace = models.ForeignKey(
        to='workspace.Workspace',
        verbose_name='Workspace',
        on_delete=models.CASCADE,
        related_name='position_workspace',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'workspace_position'
        verbose_name_plural = 'Chức vụ'
        verbose_name = 'Chức vụ'
        ordering = ['-created_at']
        unique_together = [['workspace', 'code']]

    def __str__(self):
        if self.workspace:
            return f"{self.name} ({self.code}) - {self.workspace.name}"
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        self.is_default = not self.workspace
        super().save(*args, **kwargs)


class Action(models.Model):
    name = models.CharField(
        verbose_name='Tên hành động',
        error_messages=ErrorMessages.CharField('Tên hành động', 255),
        max_length=255,
        db_index=True,
    )
    code = models.CharField(
        verbose_name='Mã hành động',
        error_messages=ErrorMessages.CharField('Mã hành động', 100),
        max_length=100,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Mô tả',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Hành động'
        db_table = 'workspace_action'
        verbose_name = 'Hành động'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})" 