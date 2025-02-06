from django.urls import path
from .views import (
    LoginView, RegisterView, ConfirmNumberView, ForgotPasswordView, ForgotPasswordChangePasswordView, DashboardView,
    logoutView, ChangePasswordView, NotificationView, NotificationDetailsView, NotificationDeleteView)


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
    path('profile/notification', NotificationView.as_view(), name='notification'),
    path('profile/notification/<int:pk>', NotificationDetailsView.as_view(), name='notification-details'),
    path('profile/notification/<int:pk>/delete', NotificationDeleteView.as_view(), name='notification-delete'),
    path('logout/', logoutView, name='logout'),
]
