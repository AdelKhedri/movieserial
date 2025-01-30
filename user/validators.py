from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


def validate_phone(value:str):
    if not value.isnumeric():
        raise ValidationError('نام کاربری نباید فقط عددی باشد')
    elif len(value) != 11 or value[:2] != '09':
        raise ValidationError('شماره تلفن نادرست است.')
    return value


def validate_unique_email(value):
    if get_user_model().objects.filter(email=value).exists():
        raise ValidationError('ایمیل تکراری است.')
    return value

def validate_unique_username(value):
    if get_user_model().objects.filter(username=value).exists():
        raise ValidationError('نام کاربری تکراری است.')
    return value

def validate_number_exist(value):
    if get_user_model().objects.filter(number=value).exists():
        raise ValidationError('شماره تلفن تکراری است.')
    return value
