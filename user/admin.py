from django.contrib import admin
from .models import User


@admin.register(User)
class UserRegister(admin.ModelAdmin):
    list_display = ['username', 'number', 'is_active', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username']


