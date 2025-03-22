from django.db import models


class Logs(models.Model):
    class Meta:
        managed = False
        verbose_name = "Nhật ký hệ thống"
        verbose_name_plural = "Nhật ký hệ thống"