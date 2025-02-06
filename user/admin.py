from django.contrib import admin
from .models import Notification, Profile, User, ForgotPasswordLink
from django.utils.html import format_html


@admin.register(User)
class UserRegister(admin.ModelAdmin):
    list_display = ['username', 'number', 'is_active', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username']


@admin.register(ForgotPasswordLink)
class UserRegister(admin.ModelAdmin):
    list_display = [field.name for field in ForgotPasswordLink._meta.fields ]
    list_display_links = ['link']


@admin.register(Notification)
class NotificationRegister(admin.ModelAdmin):
    list_display = [field.name for field in Notification._meta.fields ]
    list_filter = ['status']
    list_display_links = ['id', 'user']


@admin.register(Profile)
class Profileister(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields ]
    list_display += ['get_image']
    list_display_links = ['id', 'user']

    def get_image(self, obj):
        profile_img = obj.picture.url if obj.picture else ''
        return format_html(f'<img src="{profile_img}" style="width:100px;height:100px;border-radius:50px;">')

