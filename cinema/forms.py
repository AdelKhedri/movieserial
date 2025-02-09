from django import forms
from django.forms import formset_factory


class CommentForm(forms.Form):
    message = forms.CharField(label='نظرتون', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'نظرتون رو با بقیه به اشتراک بگذارید.'}))
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)
