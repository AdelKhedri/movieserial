from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Movie, Comment
from .forms import CommentForm


class MovieDetailsView(View):
    template_name = 'cinema/movie-details.html'
    
    def setup(self, request, *args, **kwargs):
        self.movie = get_object_or_404(Movie, Q(release_date__gte=timezone.now()) | Q(release_date__isnull=True), **kwargs)
        comment_count = Comment.objects.filter(accepted=True, media_type='movie', media_id=self.movie.id).count()
        comments = Comment.objects.filter(parent__isnull=True, accepted=True, media_type='movie', media_id=self.movie.id)
        # TODO: show Pending comments for sender 

        self.context = {
            'movie': self.movie,
            'comments': comments,
            'comment_count': comment_count,
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
