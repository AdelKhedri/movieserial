from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(label='نام کاربری', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'}))
    password = forms.CharField(label='پسورد', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'پسورد'}))
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
