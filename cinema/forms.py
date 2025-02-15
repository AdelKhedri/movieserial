from django import forms


class CommentForm(forms.Form):
    message = forms.CharField(label='نظرتون', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'نظرتون رو با بقیه به اشتراک بگذارید.'}))
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)
