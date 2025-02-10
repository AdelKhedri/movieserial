from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Country, MediaBookmark, Movie, Comment, Geners
from .forms import CommentForm
from .filters import MovieFilter


def paginate_objects(resutl, per_page, page):
    pagintor = Paginator(resutl, per_page)
    return pagintor.get_page(page)


class MovieDetailsView(View):
    template_name = 'cinema/movie-details.html'
    
    def setup(self, request, *args, **kwargs):
        self.movie = get_object_or_404(Movie, Q(release_date__gte=timezone.now()) | Q(release_date__isnull=True), **kwargs)
        comment_count = Comment.objects.filter(accepted=True, media_type='movie', media_id=self.movie.id).count()
        comments = Comment.objects.filter(parent__isnull=True, accepted=True, media_type='movie', media_id=self.movie.id)
        is_bookmarked = MediaBookmark.objects.filter(user=request.user, media_type='movie', media_id=self.movie.pk).exists()
        # TODO: show Pending comments for sender 

        self.context = {
            'movie': self.movie,
            'comments': comments,
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            'comment_count': comment_count,
            'bookmark': is_bookmarked,
            'comment_form': CommentForm(),
        }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                parent_id = comment_form.cleaned_data.get('parent', None)
                parent = Comment.objects.filter(id=parent_id).first()

                message = comment_form.cleaned_data['message']
                comment = Comment(user=request.user, message=message, parent=parent, media_type='movie', media_id=self.movie.id)
                if parent:
                    comment.parent = parent
                comment.save()
                self.context['msg'] = 'send comment success'
            else:
                self.context['comment_form'] = comment_form
        return render(request, self.template_name, self.context)


class FilterMovieView(View):
    template_name = 'cinema/movies-filter.html'

    def get(self, request, *args, **kwargs):
        movies = Movie.objects.all()
        filters = MovieFilter(request.GET, movies)
        page = request.GET.get('page', None)

        context = {
            'page_title': 'فیلتر فیلم ها',
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            'movies': paginate_objects(filters.qs, 15, page),
            'filters': filters
        }
        return render(request, self.template_name, context)


class ToggleBookmarkMovieView(View):
    def get(self, request, *args, **kwargs):
        movie = get_object_or_404(Movie, slug=kwargs['slug'])
        bookmark, result = MediaBookmark.objects.get_or_create(user=request.user, media_type='movie', media_id=movie.pk)
        if not result: bookmark.delete()
        return redirect(reverse('movie:details', kwargs={'slug': movie.slug}))
