from django.urls import path
from .views import LoginView, RegisterView, ConfirmNumberView


app_name = 'user'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', RegisterView.as_view(), name='register'),
    path('signup/confirm/', ConfirmNumberView.as_view(), name='confirm-number'),
]
