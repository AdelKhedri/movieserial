from django.urls import path
from .views import MovieDetailsView, FilterMovieView, ToggleBookmarkMovieView


app_name = 'movie'
urlpatterns = [
    path('<slug:slug>/', MovieDetailsView.as_view(), name='details'),
    path('', FilterMovieView.as_view(), name='movie'),
    path('<slug:slug>/bookmark', ToggleBookmarkMovieView.as_view(), name='toggle-bookmark-movie'),

]
