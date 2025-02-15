from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Country, MediaBookmark, Movie, Comment, Geners, Serial
from .forms import CommentForm
from .filters import MovieFilter, SerialFilter


def paginate_objects(resutl, per_page, page):
    pagintor = Paginator(resutl, per_page)
    return pagintor.get_page(page)


class MovieDetailsView(View):
    template_name = 'cinema/movie-details.html'
    
    def setup(self, request, *args, **kwargs):
        self.movie = get_object_or_404(Movie, Q(release_date__gte=timezone.now()) | Q(release_date__isnull=True), **kwargs)
        comment_count = Comment.objects.filter(accepted=True, media_type='movie', media_id=self.movie.id).count()
        comments = Comment.objects.filter(parent__isnull=True, accepted=True, media_type='movie', media_id=self.movie.id)
        is_bookmarked = MediaBookmark.objects.filter(user=request.user, media_type='movie', media_id=self.movie.pk).exists() if request.user.is_authenticated else False
        # TODO: show Pending comments for sender 

        self.context = {
            'movie': self.movie,
            'comments': comments,
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            'comment_count': comment_count,
            'is_bookmarked': is_bookmarked,
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


class FilterMediaView(View):
    template_name = 'cinema/movies-filter.html'

    def get(self, request, *args, **kwargs):
        if kwargs['media_type'] not in ['movie', 'serial']:
            raise Http404()
        
        model = Movie if kwargs['media_type'] == 'movie' else Serial
        media = model.objects.all()
        filters = MovieFilter(request.GET, media) if model == Movie else SerialFilter(request.GET, media)
        page = request.GET.get('page', None)

        context = {
            'page_title': 'فیلتر فیلم ها',
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            # 'movies': paginate_objects(filters.qs, 15, page),
            'media': paginate_objects(filters.qs, 15, page),
            'filters': filters
        }
        return render(request, self.template_name, context)


class ToggleBookmarkMediaView(View):
    def get(self, request, *args, **kwargs):
        if kwargs['media_type'] not in ['movie', 'serial']:
            raise Http404()

        model = Movie if kwargs['media_type'] == 'movie' else Serial
        media = get_object_or_404(model, slug=kwargs['slug'])
        bookmark, result = MediaBookmark.objects.get_or_create(user=request.user, media_type=model.__name__.lower(), media_id=media.pk)
        if not result: bookmark.delete()
        next_url = request.GET.get('next', None)
        next_page = next_url if next_url and next_url != reverse('media:toggle-bookmark-media', kwargs={'slug': media.slug, 'media_type': model.__name__.lower()}) else None
        return redirect(next_page) if next_page else redirect(reverse(f'media:{model.__name__.lower()}-details', kwargs={'slug': media.slug}))


class SerialDetailsView(View):
    template_name = 'cinema/serial-details.html'

    def setup(self, request, *args, **kwargs):
        self.serial = get_object_or_404(Serial, slug=kwargs['slug'])
        comments = Comment.objects.filter(parent__isnull = True, media_type = 'serial', media_id = self.serial.pk, accepted = True)
        comment_count = Comment.objects.filter(accepted = True, media_type = 'serial', media_id = self.serial.pk).count()
        is_bookmarked = MediaBookmark.objects.filter(user = request.user, media_type = 'serial', media_id = self.serial.pk).exists() if request.user.is_authenticated else False

        self.context = {
            'serial': self.serial,
            'comments': comments,
            'comment_form': CommentForm(),
            'comment_count': comment_count,
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            'is_bookmarked': is_bookmarked
        }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                parent_id = comment_form.cleaned_data.get('parent', None)
                message = comment_form.cleaned_data['message']
                parent = Comment.objects.filter(id=parent_id).first()
                comment = Comment.objects.create(message = message, media_type = 'serial', media_id = self.serial.pk, user = request.user)

                if parent:
                    comment.parent = parent
                self.context['msg'] = 'send comment success'
                comment.save()
            else:
                self.context['comment'] = comment_form
        return render(request, self.template_name, self.context)


class EpisodeDetailsView(View):
    template_name = 'cinema/serial-details.html'

    def setup(self, request, *args, **kwargs):
        self.serial = get_object_or_404(Serial, slug=kwargs['slug'])
        section = get_object_or_404(self.serial.sections, pk=kwargs['section_pk'])
        episode = get_object_or_404(section.episodes, pk=kwargs['episode_pk'])
        comments = Comment.objects.filter(parent__isnull = True, media_type = 'serial', media_id = self.serial.pk, accepted = True)
        comment_count = Comment.objects.filter(media_type = 'serial', media_id = self.serial.pk, accepted = True).count()
        is_bookmarked = MediaBookmark.objects.filter(user = request.user, media_type = 'serial', media_id = self.serial.pk).exists() if request.user.is_authenticated else False

        self.context = {
            'serial': self.serial,
            'episode': episode,
            'section': section,
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(), 
            'comments': comments,
            'comment_count': comment_count,
            'comment_form': CommentForm(),
            'is_bookmarked': is_bookmarked,
        }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                parent_id = comment_form.cleaned_data.get('parent', None)
                message = comment_form.cleaned_data['message']
                comment = Comment(message = message, media_type = 'serial', media_id = self.serial.pk, user=request.user)
                parent = Comment.objects.filter(id=parent_id).first()
                if parent:
                    comment.parent = parent
                comment.save()
                self.context['msg'] = 'send comment success'
            else:
                self.context['msg'] = comment_form
        return render(request, self.template_name, self.context)

