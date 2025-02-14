from django import forms
from django.forms import formset_factory
from .models import ContactUs


class CommentForm(forms.Form):
    message = forms.CharField(label='نظرتون', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'نظرتون رو با بقیه به اشتراک بگذارید.'}))
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)


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
