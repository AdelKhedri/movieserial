from django.urls import path
from .views import (
    LoginView, RegisterView, ConfirmNumberView, ForgotPasswordView, ForgotPasswordChangePasswordView, DashboardView,
    logoutView, ChangePasswordView)


app_name = 'user'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', RegisterView.as_view(), name='register'),
    path('signup/confirm/', ConfirmNumberView.as_view(), name='confirm-number'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('forgot-password/<str:link>/', ForgotPasswordChangePasswordView.as_view(), name='forgot-password-change-password'),

    # Dahsboard
    path('profile/', DashboardView.as_view(), name='profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', logoutView, name='logout'),
]
