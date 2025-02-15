from django import forms
from cinema.models import ContactUs


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'آدرس ایمیل'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'cols': 30, 'rows': 5, 'placeholder': 'متن پیام'}),
        }
