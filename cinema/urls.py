from django.urls import path
from .views import MovieDetailsView, FilterMediaView, SerialDetailsView, ToggleBookmarkMediaView, EpisodeDetailsView


app_name = 'media'
urlpatterns = [
    path('movie/<slug:slug>/', MovieDetailsView.as_view(), name='movie-details'),
    path('<str:media_type>/', FilterMediaView.as_view(), name='media-filter'),
    path('<str:media_type>/<slug:slug>/bookmark', ToggleBookmarkMediaView.as_view(), name='toggle-bookmark-media'),
    path('serial/<slug:slug>/', SerialDetailsView.as_view(), name='serial-details'),
    path('serial/<slug:slug>/<int:section_pk>/<int:episode_pk>/', EpisodeDetailsView.as_view(), name='serial-details-episode'),
]
