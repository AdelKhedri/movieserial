from django.contrib import admin
from .models import User, ForgotPasswordLink


@admin.register(User)
class UserRegister(admin.ModelAdmin):
    list_display = ['username', 'number', 'is_active', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username']


@admin.register(ForgotPasswordLink)
class UserRegister(admin.ModelAdmin):
    list_display = [field.name for field in ForgotPasswordLink._meta.fields ]
    list_display_links = ['link']

