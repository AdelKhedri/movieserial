from django.urls import path
from .views import MovieDetailsView, FilterMovieView, SerialDetailsView, ToggleBookmarkMovieView, EpisodeDetailsView


app_name = 'media'
urlpatterns = [
    path('movie/<slug:slug>/', MovieDetailsView.as_view(), name='movie-details'),
    path('movie/', FilterMovieView.as_view(), name='movie'),
    path('movie/<slug:slug>/bookmark', ToggleBookmarkMovieView.as_view(), name='toggle-bookmark-movie'),
    path('serial/<slug:slug>/', SerialDetailsView.as_view(), name='serial-details'),
    path('serial/<slug:slug>/<int:section_pk>/<int:episode_pk>/', EpisodeDetailsView.as_view(), name='serial-details-episode'),

]
