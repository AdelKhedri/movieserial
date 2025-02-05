from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.core.exceptions import ValidationError
from .models import Profile, User
from django.contrib.auth import authenticate
from .validators import validate_number_exist, validate_unique_email, validate_unique_username


class LoginForm(forms.Form):
    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "نام کاربری"}
        ),
    )
    password = forms.CharField(
        label="پسورد",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "پسورد"}),
    )
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class RegisterForm(forms.ModelForm):
    accept_rules = forms.BooleanField(label='پذیرش قوانین سایت', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    password1 = forms.CharField(label='پسورد', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='تکرار پسورد', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='نام کاربری', validators=[validate_unique_username], widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label='ایمیل', validators=[validate_unique_email], widget=forms.TextInput(attrs={'class': 'form-control'}))
    number = forms.CharField(label='شماره', validators=[validate_number_exist], widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "number"]

    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = self.cleaned_data
        password1, password2 = cleaned_data.get("password1", None), cleaned_data.get("password2", None)
        username = cleaned_data.get("username", None)

        if (
            not password1
            or not password2
            or len(password1) < 7
            or password1 == username
            or password1.isnumeric()
            or password1.isalpha()
        ):
            raise ValidationError("لطفا موارد رو رعایت کنید.")
        if password1 != password2:
            raise ValidationError('پسورد ها با هم مطابقت ندارند.')

        return cleaned_data

    def clean_accept_rules(self):
        accept_rules = self.cleaned_data.get('accept_rules')
        if not accept_rules:
            raise ValidationError('شما باید قوانین را بپذیرید.')
        return accept_rules


class RecaptchaForm(forms.Form):
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class ChangePasswordForgotPasswordFrom(forms.Form):
    password1 = forms.CharField(label='پسورد', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='تکرار پسورد', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = self.cleaned_data
        password1, password2 = cleaned_data.get("password1", None), cleaned_data.get("password2", None)

        if (
            not password1
            or not password2
            or len(password1) < 7
            or password1.isnumeric()
            or password1.isalpha()
        ):
            raise ValidationError("لطفا موارد رو رعایت کنید.")
        if password1 != password2:
            raise ValidationError('پسورد ها با هم مطابقت ندارند.')
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', ]
    
        widgets = {
            'picture': forms.FileInput(attrs={'class': 'profile-file-input'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'number']
    
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ChangePasswordForm(ChangePasswordForgotPasswordFrom):
    last_password = forms.CharField(label='پسورد قبلی', max_length=150, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def save(self, user):
        password = self.cleaned_data['password1']
        user.set_password(password)
        user.save()
        return user
