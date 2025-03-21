from django_currentuser.middleware import get_current_user
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.db import models

from utils.exception import MessageError
from constants.response_messages import ResponseMessage


class BaseModel(models.Model):
    updated_at = models.DateTimeField(verbose_name="Thời gian cập nhật", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Thời gian tạo", auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Ghi đè phương thức save để cập nhật updated_at và các trường người dùng
        """

        # Thiết lập thời gian sửa đổi
        is_update = self.pk is not None
        if is_update:
            self.updated_at = timezone.now()

        current_user = None
        if hasattr(self, "created_by") or hasattr(self, "updated_by"):
            current_user = get_current_user()
            auth_user_model = current_user.__class__.__name__
            if auth_user_model == "AdminUser":
                current_user = None
        
        is_login = current_user and not isinstance(current_user, AnonymousUser)

        # Xử lý trường created_by nếu có
        if hasattr(self, "created_by") and is_login and self.created_by is None:
            setattr(self, "created_by", current_user)

        # Xử lý trường updated_by nếu có
        if hasattr(self, "updated_by") and is_update and is_login:
            setattr(self, "updated_by", current_user)

        super(BaseModel, self).save(*args, **kwargs)


class BaseModelSoftDelete(BaseModel):
    is_delete = models.BooleanField(verbose_name="Đã xóa", default=False)
    deleted_at = models.DateTimeField(verbose_name="Thời gian xóa", blank=True, null=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard_delete=False, delete_keys=[]):
        """
        Ghi đè phương thức delete để hỗ trợ xóa mềm

        Args:
            using: Database connection to use
            keep_parents: Giữ lại object cha hay không
            hard_delete: Xóa cứng thay vì xóa mềm

        Raises:
            MessageError: Nếu object đã bị xóa
        """

        if hard_delete:
            super(BaseModelSoftDelete, self).delete(using, keep_parents)
            return

        if self.is_delete:
            raise MessageError(ResponseMessage.DELETED_ERROR)

        self.deleted_at = timezone.now()
        self.is_delete = True

        # Cập nhật flag __deleted__ cho người dùng bị xóa
        deleted_flag = f"__deleted__{self.pk}"
        for delete_key in delete_keys:
            delete_key_value = getattr(self, delete_key, None)

            if not delete_key_value or not isinstance(delete_key_value, str):
                continue

            if self.is_delete and not delete_key_value.endswith(deleted_flag):
                setattr(self, delete_key, f"{delete_key_value}{deleted_flag}")

        # Cập nhật người xóa nếu có
        if hasattr(self, "deleted_by"):
            current_user = get_current_user()
            if current_user and not isinstance(current_user, AnonymousUser):
                auth_user_model = current_user.__class__.__name__
                if auth_user_model != "AdminUser":
                    self.deleted_by = current_user
                    self.deleted_by = current_user

        super(BaseModelSoftDelete, self).save()

    def save(self, *args, **kwargs):
        if self.is_delete and self.deleted_at is None:
            self.deleted_at = timezone.now()

            # Cập nhật người xóa nếu có
            if hasattr(self, "deleted_by"):
                current_user = get_current_user()
                if current_user and not isinstance(current_user, AnonymousUser):
                    auth_user_model = current_user.__class__.__name__
                    if auth_user_model != "AdminUser":
                        self.deleted_by = current_user

        if not self.is_delete and self.deleted_at is not None:
            self.deleted_at = None

            # Xóa thông tin người xóa nếu có
            if hasattr(self, "deleted_by") and self.deleted_by is not None:
                self.deleted_by = None

        super(BaseModelSoftDelete, self).save(*args, **kwargs)

    @classmethod
    def all_objects(cls):
        """
        Trả về tất cả đối tượng bao gồm cả đã xóa

        Returns:
            QuerySet: Queryset chứa tất cả đối tượng
        """
        return cls.objects.all()

    @classmethod
    def active_objects(cls):
        """
        Trả về các đối tượng chưa bị xóa

        Returns:
            QuerySet: Queryset chứa các đối tượng chưa bị xóa
        """
        return cls.objects.filter(is_delete=False)

    @classmethod
    def deleted_objects(cls):
        """
        Trả về các đối tượng đã bị xóa

        Returns:
            QuerySet: Queryset chứa các đối tượng đã bị xóa
        """
        return cls.objects.filter(is_delete=True)


class ManagerSoftDeleteMixin:
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)
