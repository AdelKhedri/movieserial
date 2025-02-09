from django.urls import path
from .views import MovieDetailsView


app_name = 'movie'
urlpatterns = [
    path('<slug:slug>/', MovieDetailsView.as_view(), name='details'),
]
