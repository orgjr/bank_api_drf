from django.contrib.auth.base_user import BaseUserManager as DjangoBaseUserManager
from django.contrib.auth.password_validation import validate_password


class UserManager(DjangoBaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("email is required.")

        if not password:
            raise ValueError("Password is required.")

        email = self.normalize_email(email.lower().strip())

        user = self.model(email=email, **extra_fields)

        validate_password(password)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have staff authority.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have superuser authority.")

        return self.create_user(email, password, **extra_fields)
