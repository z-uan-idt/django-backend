from django.contrib.auth.models import BaseUserManager


class AdminUserManager(BaseUserManager):
    def create_user(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, full_name, password, **extra_fields):
        return self.create_user(
            full_name=full_name,
            username=username,
            password=password,
            **extra_fields
        )

    def get_by_natural_key(self, username):
        return self.get(**{"username__iexact": username})
