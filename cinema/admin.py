from django.contrib import admin
from .models import Movie, Ganers, DownloadLink, Agents, Comment
from django.utils.html import format_html


@admin.register(Movie)
class MovieRegister(admin.ModelAdmin):
    list_display = ['persian_name', 'year_create', 'country', 'imdb_link', 'slug', 'get_image']
    filter_horizontal = ['stars', 'geners', 'links', 'likes', 'dislikes', 'related_movies']
    list_filter = ['geners']
    search_fields = ['perisan_name', 'english_name', 'discription']
    autocomplete_fields = ['director']
    prepopulated_fields = {'slug': ('english_name', 'year_create')}
    list_select_related = ['director']
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('geners', 'stars', 'links', 'likes', 'dislikes',)

    def get_image(self, obj):
        return format_html(f'<img src="{obj.baner.url}" with="150px" height="150px">')


@admin.register(Ganers)
class GanersRegister(admin.ModelAdmin):
    list_display = [field.name for field in Ganers._meta.fields]
    search_fields = ['name']


@admin.register(DownloadLink)
class DownloadLinkRegister(admin.ModelAdmin):
    list_display = [field.name for field in DownloadLink._meta.fields]
    list_filter = ['is_subtitle', 'subtitle_type', 'is_persian_sound']
    show_full_result_count = False


@admin.register(Agents)
class AgentsRegister(admin.ModelAdmin):
    list_display = [field.name for field in Agents._meta.fields]
    search_fields = ['director']
    show_full_result_count = False


@admin.register(Comment)
class AgentsRegister(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.fields]
    list_filter = ['accepted', 'media_type']
    list_select_related = ['user', 'parent']
    show_full_result_count = False
    search_fields = ['message']