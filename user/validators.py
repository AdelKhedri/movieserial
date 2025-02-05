from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from string import ascii_letters


def validate_phone(value:str):
    if not value.isnumeric():
        raise ValidationError('نام کاربری نباید فقط عددی باشد')
    elif len(value) != 11 or value[:2] != '09':
        raise ValidationError('شماره تلفن نادرست است.')
    return value

ascii_letters_with_numbers = ascii_letters + '0987654321'
def validate_username(username: str):
    if username.isnumeric() or username[0] not in ascii_letters:
        raise ValidationError('نام کاربری نمیتواند با عدد شروع شود یا تماما عدد باشد')
    elif len(username) < 4:
        raise ValidationError('نام کاربری باید حداقل 4 کارکتر باشد')
    elif any(ch not in ascii_letters_with_numbers for ch in username): raise ValidationError('نام کاربری باید انگلیسی باشد.')


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
