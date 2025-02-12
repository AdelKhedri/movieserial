from user.tests.tests_views import BaseTestCase
from ..models import Agents, Country, DownloadLink, Episode, Geners, Movie, Comment, Section, Serial
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

        self.url = reverse('media:movie-details', kwargs={'slug': movie.slug})

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


class TestSerialDetailsView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.media_name = 'test.jpg'
        self.poster = SimpleUploadedFile(
            name = self.media_name,
            content = b'',
            content_type = 'image/jpeg'
        )
        serial = Serial.objects.create(
            persian_name = 'تست',
            english_name = 'test',
            year_create = 2022,
            slug = 'test',
            imdb_link = 'https://imdb.com/title/45656',
            imdb_point = 2.2,
            baner = self.poster
            )
        self.url = reverse('media:serial-details', kwargs={'slug': serial.slug})

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'cinema/serial-details.html')


    def test_send_comment_success(self):
        res = self.client.post(self.url, data={'message': 'test'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def test_send_comment_success_with_parent(self):
        Comment.objects.create(user=self.user, message='test',media_type='movie', media_id=1)
        res = self.client.post(self.url, data={'message': 'test', 'parent': '1'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def test_send_comment_failed_loginrequired(self):
        self.client.get(reverse('user:logout'))
        res = self.client.post(self.url, data={'message': 'test'})
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def tearDown(self):
        os.remove(f'media/images/serials/{self.media_name}')


class TestEpisodeDetailsView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.baner_name = 'test.jpg'
        self.baner_name2 = 'test2.jpg'
        baner = SimpleUploadedFile(self.baner_name, b'', 'image/jpeg')
        baner2 = SimpleUploadedFile(self.baner_name2, b'', 'image/jpeg')
        country = Country.objects.create(name='name', slug='slug')
        director = Agents.objects.create(name='name', role='director')
        gener = Geners.objects.create(name='name', slug='slug')
        link = DownloadLink.objects.create(quality='1080p', link='http://test.test/', subtitle_type='nosub', is_persian_sound=False)
        episode = Episode.objects.create(name='test', baner=baner2, time='02:02:02')
        episode.links.set([link])
        section = Section.objects.create(name = 'S1', status = 'createing')
        section.episodes.set([episode])

        self.serial = Serial.objects.create(
            persian_name = 'تست',
            english_name = 'test',
            year_create = 2023,
            slug = 'test',
            imdb_point = 2.6,
            baner = baner,
            director = director,
            quality = '4K',
            last_episod = 'قسمت 1'
        ) # id is 1 i know
        self.serial.countrys.set([country.id])
        self.serial.geners.set([gener.id])
        self.serial.sections.set([episode.id])
        
        self.url = reverse(
                'media:serial-details-episode',
                kwargs={
                    'slug': self.serial.slug,
                    'section_pk': section.pk, 
                    'episode_pk': episode.pk}
            )

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'cinema/serial-details.html')

    def test_send_comment_success(self):
        res = self.client.post(self.url, data={'message': 'test'})
        self.assertContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')

    def test_send_comment_success_with_parent(self):
        comment = Comment.objects.create(message='test1', media_type='serial', media_id=self.serial.pk, user=self.user, accepted=True)
        res = self.client.post(self.url, data={'message': 'test', 'parent': comment.pk}) # pk is 1
        self.assertContains(res, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده میشود')
        self.assertEqual(Comment.objects.get(parent=comment).message, 'test')

    def tearDown(self):
        baners = [self.baner_name, self.baner_name2]
        for baner in baners:
            os.remove('media/images/serials/' + baner)