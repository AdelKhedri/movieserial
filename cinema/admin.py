from django.contrib import admin
from .models import Movie, Geners, DownloadLink, Agents, Comment, Country, MediaBookmark, Serial, Section, Episode
from django.utils.html import format_html


@admin.register(Movie)
class MovieRegister(admin.ModelAdmin):
    list_display = ['persian_name', 'year_create', 'get_countrys', 'slug', 'get_geners', 'imdb_link',  'get_image', ]
    filter_horizontal = ['stars', 'geners', 'links', 'likes', 'dislikes', 'related_movies', 'countrys']
    list_filter = ['geners']
    search_fields = ['perisan_name', 'english_name', 'discription']
    autocomplete_fields = ['director']
    prepopulated_fields = {'slug': ('english_name', 'year_create')}
    list_select_related = ['director']
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('geners', 'stars', 'links', 'likes', 'dislikes', 'countrys', 'related_movies')

    def get_image(self, obj):
        return format_html(f'<img src="{obj.baner.url}" with="150px" height="150px">')

    def get_countrys(self, obj):
        return format_html(''.join(
            [f'<span style="background-color: #38ff28; border-radius: 7px;padding: 3px 6px; margin-right:4px;">{countrys.name}</span>' for countrys in obj.countrys.all()]
            ))
    
    def get_geners(self, obj):
        return format_html(''.join(
            [f'<span style="background-color: #38ff28; border-radius: 7px;padding: 3px 6px; margin-right:4px;">{gener.name}</span>' for gener in obj.geners.all()]
            ))
    


@admin.register(Geners)
class GenersRegister(admin.ModelAdmin):
    list_display = [field.name for field in Geners._meta.fields]
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


@admin.register(Country)
class CountryRegister(admin.ModelAdmin):
    list_display = [field.name for field in Country._meta.fields]


@admin.register(MediaBookmark)
class MediaBookmarkRegister(admin.ModelAdmin):
    list_display = [field.name for field in MediaBookmark._meta.fields] + ['get_media_object']


@admin.register(Episode)
class EpisodeRegister(admin.ModelAdmin):
    list_display = [field.name for field in Episode._meta.fields]
    filter_horizontal = ['links']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('links')


@admin.register(Section)
class SectionRegister(admin.ModelAdmin):
    list_display = [field.name for field in Section._meta.fields]
    filter_horizontal = ['episodes']
    list_filter = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('episodes')


@admin.register(Serial)
class SerialRegister(admin.ModelAdmin):
    list_display = ['persian_name' , 'year_create', 'get_countrys', 'get_baner', 'imdb_point', 'get_geners']
    filter_horizontal = ['countrys', 'geners', 'dislikes', 'likes', 'stars', 'related_serials', 'sections']
    list_filter = ['quality']
    list_select_related = ['director']
    prepopulated_fields = {'slug': ('english_name', 'year_create',)}

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('countrys', 'geners', 'dislikes', 'likes', 'stars', 'related_serials', 'sections')

    def get_baner(self, obj):
        return format_html(f'<img src="{obj.baner.url}" with="150px" height="150px">')

    def get_countrys(self, obj):
        return format_html(''.join(
            [f'<span style="background-color: #38ff28; border-radius: 7px;padding: 3px 6px; margin-right:4px;">{countrys.name}</span>' for countrys in obj.countrys.all()]
            ))
    
    def get_geners(self, obj):
        return format_html(''.join(
            [f'<span style="background-color: #38ff28; border-radius: 7px;padding: 3px 6px; margin-right:4px;">{gener.name}</span>' for gener in obj.geners.all()]
            ))
