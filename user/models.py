from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from .validators import validate_phone, validate_username
from django.core.exceptions import ValidationError
from uuid import uuid4


class Manager(UserManager):

    def create_user(self, number, username, email, password=None, **extra_fields):
        if not password:
            raise ValidationError("user must have password.")
        elif not number:
            raise ValidationError("user must have a unique phone")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.number = number
        user.username = username
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, number, username, email, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(number, username, email, password, **extra_fields)


class User(AbstractUser):
    number = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_phone],
        verbose_name="شماره تلفن",
    )
    is_active = models.BooleanField(default=False, verbose_name="فعال")
    special_time = models.DateTimeField(null=True, verbose_name="زمان اشتراک")
    email = models.EmailField(unique=True, verbose_name="ایمیل")
    username = models.CharField(max_length=150, validators=[validate_username], unique=True, verbose_name='نام کاربری')
    balance = models.IntegerField(default=900000, verbose_name='موجودی')

    REQUIRED_FIELDS = ["number", "email"]
    objects = Manager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربر ها "

    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username


class ForgotPasswordLink(models.Model):
    link = models.UUIDField(default=uuid4, verbose_name='لینک')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    time = models.DateTimeField(verbose_name='زمان ارسال لینک')

    class Meta:
        verbose_name = 'لینک بازیابی رمز عبور'
        verbose_name_plural = 'لینک های بازیابی رمز عبور'


    def __str__(self):
        return self.user.__str__()


class Profile(models.Model):
    gender_types = (('femal', 'مرد'), ('mel', 'زن'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    picture = models.ImageField(blank=True, upload_to='images/', verbose_name='عکس')
    gender = models.CharField(blank=True, choices=gender_types, default='femal', max_length=5, verbose_name='جنسیت')
    about = models.TextField(blank=True, verbose_name='درباره')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'
        ordering = []

    def __str__(self):
        return self.user.__str__()


class Notification(models.Model):
    status_list = (('read', 'خوانده'), ('new', 'جدید'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    message = models.TextField(verbose_name='پیام')
    time = models.DateTimeField(auto_now_add=True, verbose_name='زمان')
    status = models.CharField(choices=status_list, default='new', max_length=4, verbose_name='وضعیت')

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلانات'
        ordering = ['time']


    def __str__(self):
        return self.user.__str__()


class Package(models.Model):
    name = models.CharField(max_length=150, verbose_name='موضوع')
    price = models.IntegerField(verbose_name='قیمت')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    days = models.IntegerField(verbose_name='روز ها')
    tax = models.IntegerField(default=0, verbose_name='مالیات')
    discount = models.IntegerField(blank=True, null=True, verbose_name='تخفیف')
    color_types = (('red', 'قرمز'), ('green', 'سبز'), ('sky', 'آبی آسمانی'))
    color = models.CharField(max_length=5, choices=color_types, default='sky', verbose_name='رنگ')

    def get_final_price(self):
        return self.price + self.tax if self.discount is None else self.price + self.tax - self.discount

    class Meta:
        verbose_name = 'پکیج'
        verbose_name_plural = 'پکیج ها'

    def __str__(self):
        return self.name


class HistoryOfSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, verbose_name='پکیج')
    time = models.DateTimeField(auto_now_add=True, verbose_name='زمان')
    payed = models.BooleanField(default=False, verbose_name='وضعیت پرداخت')
    final_price = models.IntegerField(verbose_name='قیمت نهایی')
    days = models.IntegerField(verbose_name='روز ها')

    class Meta:
        verbose_name = 'سابقه پکیج'
        verbose_name_plural = 'سابقه پکیج ها'

    def __str__(self):
        return self.package.__str__()
