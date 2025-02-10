from django.urls import path
from .views import MovieDetailsView, FilterMovieView


app_name = 'movie'
urlpatterns = [
    path('<slug:slug>/', MovieDetailsView.as_view(), name='details'),
    path('', FilterMovieView.as_view(), name='movie'),
]
