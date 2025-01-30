from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from .validators import validate_phone, validate_number_exist, validate_unique_username, validate_unique_email
from django.core.exceptions import ValidationError


class Manager(UserManager):

    def create_user(self, number, email, password=None, **extra_fields):
        if not password:
            raise ValidationError("user must have password.")
        elif not number:
            raise ValidationError("user must have a unique phone")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.number = number
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, number, email, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(number, email, password, **extra_fields)


class User(AbstractUser):
    number = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_phone, validate_number_exist],
        verbose_name="شماره تلفن",
    )
    is_active = models.BooleanField(default=False, verbose_name="فعال")
    special_time = models.DateTimeField(null=True, verbose_name="زمان اشتراک")
    email = models.EmailField(unique=True, validators=[validate_unique_email], verbose_name="ایمیل")
    username = models.CharField(max_length=150, unique=True, validators=[validate_unique_username], verbose_name='نام کاربری')

    REQUIRED_FIELDS = ["number", "email"]
    objects = Manager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربر ها "

    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username
