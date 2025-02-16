import django_filters 
from .models import Agents, Country, Geners, Movie, Serial
from django import forms


default_attr = {
    'class': 'form-control',
}

class CostumSelec():
    pass
class MovieFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['countrys'].extra['choices'] = [(countrys.id, countrys.name) for countrys in Country.objects.all()]
        self.filters['geners'].extra['choices'] = [(gener.id, gener.name) for gener in Geners.objects.all()]

    english_name = django_filters.CharFilter(
        lookup_expr='contains',
        label='نام انگلیسی',
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'padding: 10px'})
    )
    persian_name = django_filters.CharFilter(
        lookup_expr='contains',
        label='نام فارسی',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام فیلم را وارد کنید'})
    )
    year_create_lt = django_filters.CharFilter(
        lookup_expr='lt',
        label='سال ساخت کمتر از',
        field_name='year_create',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'padding: 10px'})
    )
    year_create_gt = django_filters.CharFilter(
        lookup_expr='gt',
        field_name='year_create',
        label='سال ساخت بیشتر از',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'padding: 10px'})
    )
    imdb_point_lt = django_filters.CharFilter(
        lookup_expr='lt',
        label='امتیاز imdb کمتر از',
        field_name='imdb_point',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'padding: 10px'})
    )
    imdb_point_gt = django_filters.CharFilter(
        lookup_expr='gt',
        field_name='imdb_point',
        label='امتیاز imdb بیشتر از',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'padding: 10px'})
    )
    description = django_filters.CharFilter(
        lookup_expr='contains',
        label='درباره فیلم',
        field_name='description',
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'padding: 10px'})
    )
    countrys = django_filters.MultipleChoiceFilter(
        # choices=[(countrys.id, countrys.name) for countrys in Country.objects.all()],
        label='کشور',
        lookup_expr='in',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    geners = django_filters.MultipleChoiceFilter(
        # choices = [(gener.id, gener.name) for gener in Geners.objects.all()],
        label='ژانر ها',
        lookup_expr='in',
        widget=forms.CheckboxSelectMultiple(attrs={ 'class': 'form-check-input'}),
    )
    quality = django_filters.ChoiceFilter(
        choices = [('Cam', 'پرده سینما'), ('TS', 'تی اس'), ('SD', 'SD'), ('HD', 'HD'), ('FHD', 'Full HD'), ('2K', '2K'), ('4K', '4K'), ('8K', '8K')],
        label='کیفیت',
        lookup_expr='exact',
        empty_label='یک کیفیت را انتخاب کنید',
        widget=forms.Select(attrs={'class': 'select'})
    )
    director = django_filters.ModelChoiceFilter(
        queryset = Agents.objects.filter(role='director'),
        label='کارگردان',
        lookup_expr='exact',
        empty_label='یک کارگردان را انتخاب کنید',
        widget=forms.Select(attrs={'class': 'select'}),
        to_field_name = 'id'
    )
    stars = django_filters.ModelChoiceFilter(
        queryset = Agents.objects.filter(role='actor'),
        label='بازیگران',
        lookup_expr='exact',
        empty_label='یک بازیگر را انتخاب کنید',
        widget=forms.Select(attrs={'class': 'select'}),
        to_field_name = 'id'
    )

    class Meta:
        model = Movie
        fields = ['persian_name', 'english_name', 'description', 'geners', 'quality']


class SerialFilter(MovieFilter):
    class Meta:
        model = Serial
        fields = ['persian_name', 'english_name', 'description', 'geners', 'quality']
