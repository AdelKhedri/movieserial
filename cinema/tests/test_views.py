from user.tests.tests_views import BaseTestCase
from ..models import Movie, Comment
from user.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class DetailsMovieView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.media_name = 'test.jpg'
        self.poster = SimpleUploadedFile(
            name = self.media_name,
            content = b'',
            content_type = 'image/jpeg'
        )
        movie = Movie.objects.create(
            persian_name = 'تست',
            english_name = 'test',
            year_create = 2022,
            slug = 'test',
            imdb_link = 'https://imdb.com/title/45656',
            imdb_point = 2.2,
            baner = self.poster
            )

        self.url = reverse('movie:details', kwargs={'slug': movie.slug})

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'cinema/movie-details.html')

    def test_send_comment_success(self):
        res = self.client.post(self.url, data={'message': 'test'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def test_send_comment_success_with_parent(self):
        Comment.objects.create(user=self.user, message='test',media_type='movie', media_id=1)
        self.client.force_login(self.user)
        res = self.client.post(self.url, data={'message': 'test', 'parent': '1'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def test_send_comment_failed_loginrequired(self):
        self.client.get(reverse('user:logout'))
        res = self.client.post(self.url, data={'message': 'test'})
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def tearDown(self):
        os.remove(f'media/images/movies/{self.media_name}')
