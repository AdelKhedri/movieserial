from unittest.mock import patch
from django_recaptcha.client import RecaptchaResponse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from cinema.models import Movie
from ..models import Notification, User, ForgotPasswordLink
from django.urls import reverse
from datetime import datetime, timedelta
from freezegun import freeze_time
from django.utils import timezone
import os


class BaseTestCase(TestCase):

    @patch('django_recaptcha.fields.client.submit')
    def setUp(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        self.user = User.objects.create(username='user', email='user@gmail.com', number='09123456789')
        self.user.set_password('password')
        self.user.is_active = True
        self.user.save()

        self.user_data = {
            'username': 'user',
            'password': 'password',
            'g-recaptcha-response': 'RESPONSE'
        }
        self.login_url = reverse('user:login')
        self.client.post(self.login_url, data=self.user_data)


class TestLoginView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.get(reverse('user:logout'))

    def test_url_exist(self):
        res = self.client.get(self.login_url)
        self.assertEqual(res.status_code, 200)

    def test_template(self):
        res = self.client.get(self.login_url)
        self.assertTemplateUsed(res, 'user/login.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_fail_login_user_not_exist(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        self.user_data['username'] = 'test'
        res = self.client.post(self.login_url, data=self.user_data)
        self.assertContains(res, 'خطا: نام کاربری یا پسورد نادرست است.')

    def test_failed_login_recaptcha(self):
        del self.user_data['g-recaptcha-response']
        res = self.client.post(self.login_url, data=self.user_data)
        self.assertContains(res, 'لطفا کپچا رو تایید کنید.')

    @patch('django_recaptcha.fields.client.submit')
    def test_login_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        res = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(res.wsgi_request.user.username, 'user')


class TestRegisterView(TestCase):
    def setUp(self):
        user = User.objects.create(username = 'user')
        user.set_password('pass')
        user.save()
        self.url = reverse('user:register')
        self.data = {
            'username': 'test',
            'email': 'user@gmail.com',
            'number': '09123456789',
            'password1': 'test1234',
            'password2': 'test1234',
            'g-recaptcha-response': 'mocked-captcha-response',
            'accept_rules': True
        }

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/register.html')


    @patch("django_recaptcha.fields.client.submit")
    def test_register_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        res = self.client.post(self.url, self.data)
        self.assertEqual(res.status_code, 302)

    def test_captcha_failed(self):
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'لطفا کد کچا رو حل کنید.')


class TestConfirmView(TestCase):
    def setUp(self):
        self.register_url = reverse('user:register')
        self.confirm_url = reverse('user:confirm-number')
        self.data = {
            'username': 'user',
            'email': 'user@user.user',
            'number': '09123456789',
            'password1': 'password1',
            'password2': 'password1',
            'accept_rules': True,
            'g-recaptcha-response': 'ACCEPT',
        }

    def test_redirect_not_register_user_inactive_url(self):
        res = self.client.get(self.confirm_url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('user:register'))

    @patch('django_recaptcha.fields.client.submit')
    def test_template_used(self, mocked_value):
        mocked_value.retrun_value = RecaptchaResponse(is_valid=True)
        self.client.post(self.register_url, self.data)
        res = self.client.get(self.confirm_url)
        self.assertTemplateUsed(res, 'user/confirm.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_confirm_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        res = self.client.post(self.register_url, self.data)
        code = res.wsgi_request.session.get('code')
        number = res.wsgi_request.session.get('number')

        # Redirect to confirm number
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.confirm_url)
        self.assertEqual(number, self.data['number'])

        confirm_res = self.client.post(self.confirm_url, {'code': code})
        self.assertEqual(confirm_res.status_code, 302)

        user = User.objects.get(username = self.data['username'])
        self.assertTrue(user.is_active)

    @patch('django_recaptcha.fields.client.submit')
    def test_confirm_failed_required_code(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        res = self.client.post(self.register_url, self.data)

        # Redirect to confirm number
        self.assertEqual(res.status_code, 302)

        confirm_res = self.client.post(self.confirm_url, {})
        self.assertContains(confirm_res, 'لطفا کد زا وارد کنید.')

    @patch('django_recaptcha.fields.client.submit')
    def test_confirm_failed_diffrent_code(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        res = self.client.post(self.register_url, self.data)

        # Redirect to confirm number
        self.assertEqual(res.status_code, 302)

        confirm_res = self.client.post(self.confirm_url, {'code': 2323})
        self.assertContains(confirm_res, 'کد معتبر نیست.')


class TestForgotPasswordView(TestCase):
    def setUp(self):
        user = User.objects.create(username='user', number='09123456789')
        user.set_password('pass')
        user.save()
        self.login_url = reverse('user:login')
        self.url = reverse('user:forgot-password')

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/forgot-password.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_success_send_link(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'number': '09123456789'
        }
        
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'کد با موفقیت ارسال شد.')

    @patch('django_recaptcha.fields.client.submit')
    def test_failed_send_link_number_not_found(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'number': '65231'
        }

        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'شماره موبایل اشتباه است.')

    @patch('django_recaptcha.fields.client.submit')
    def test_failed_send_link_last_sended(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'number': '09123456789'
        }

        res = self.client.post(self.url, data=data)
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'لطفا 5 دقیقه از آخرین تلاش خود صبر کنید.')


    @freeze_time(datetime.now())
    @patch('django_recaptcha.fields.client.submit')
    def test_failed_send_link_last_sended(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        start_time = datetime.now()
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'number': '09123456789'
        }

        res = self.client.post(self.url, data=data)
        
        # freeze time
        with freeze_time(start_time + timedelta(minutes=5, seconds=2)):
            res = self.client.post(self.url, data=data)
            self.assertContains(res, 'کد با موفقیت ارسال شد.')


class TestForgotPasswordChangePasswordView(BaseTestCase):
    def setUp(self):
        super().setUp()
        forgot_password_link = str(ForgotPasswordLink.objects.create(user=self.user, time=timezone.now() + timedelta(minutes=5)).link)
        self.link = forgot_password_link.replace(forgot_password_link[:4], '0000', 1)
        self.url = reverse('user:forgot-password-change-password', args=[forgot_password_link])
        self.client.get(reverse('user:logout'))

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/forgot-password.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_change_password_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'password1': 'new_pass',
            'password2': 'new_pass',
        }
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'تغییر پسورد موفقیت آمیز بود.')

    @patch('django_recaptcha.fields.client.submit')
    def test_change_password_failed_invalid_link(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        url = reverse('user:forgot-password-change-password', kwargs={'link': self.link})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)


class TestProfileView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.profile_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'number': '09123456789',
            'first_name': 'user',
            'last_name': '',
            'about': ''
        }
        User.objects.create(username='user1', email='sa@gmail.com', number='09123456788')
        self.url = reverse('user:profile')

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/profile.html')

    def test_update_username_success(self):
        res = self.client.post(self.url, data=self.profile_data)
        self.assertContains(res, 'پروفایل با موفقیت آپدیت شد.')

    def test_update_username_failed_duplicated_username(self):
        data = self.profile_data
        data['username'] = 'user1'
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'کاربر با این نام کاربری از قبل موجود است.')

    def test_update_username_failed_duplicated_email(self):
        data = self.profile_data
        data['email'] = 'sa@gmail.com'
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'کاربر با این ایمیل از قبل موجود است.')

    def test_update_username_failed_duplicated_number(self):
        data = self.profile_data
        data['number'] = '09123456788'
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'کاربر با این شماره تلفن از قبل موجود است.')


class TestLogoutView(BaseTestCase):
    def setUp(self):
        super().setUp()     
        self.url = reverse('user:logout')

    @patch('django_recaptcha.fields.client.submit')
    def test_logout_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        
        res = self.client.post(self.login_url, data=self.user_data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.wsgi_request.user.is_authenticated)
        
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(res.wsgi_request.user.is_authenticated)

    def test_login_required(self):
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('user:login'))


class TestChangePasswordView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.change_password_data = {
            'password1': 'new_pass',
            'password2': 'new_pass',
            'last_password': 'password',
        }
        self.url = reverse('user:change-password')

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/change-password.html')

    def test_change_password_success(self):
        res = self.client.post(self.url, data=self.change_password_data)
        self.assertContains(res, 'تغییر پسورد با موفقیت انجام شد.')

    def test_change_password_failed_invalid_last_password(self):
        data = self.change_password_data
        data['last_password'] = 'test'
        res = self.client.post(self.url, data=self.change_password_data)
        self.assertContains(res, 'پسورد قبلی اشتباه است.')

    def test_change_password_failed_not_matched_passwords(self):
        data = self.change_password_data
        data.update({
            'password1': 'test',
            'password2': 'tests',
            'last_password': 'asdasdas'
            })
        res = self.client.post(self.url, data=self.change_password_data)
        self.assertContains(res, 'لطفا موارد رو رعایت کنید.')


class TestNotificationView(BaseTestCase):
    def setUp(self):
        super().setUp()
        nots = []
        for counter in range(40):
            nots.append(Notification(user=self.user, message='s'*150, status='read' if counter % 2 == 0 else 'new'))
        Notification.objects.bulk_create(nots)
        self.url = reverse('user:notification')

        self.res = self.client.get(self.url)

    def test_url(self):
        self.assertEqual(self.res.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.res, 'user/notification.html')

    def test_get_own_notification(self):
        self.assertEqual(self.res.context['notification_counts'], 20)

    def test_notification_pagination(self):
        self.assertEqual(self.res.context['page_obj'].paginator.num_pages, 4)        

    def test_truncatechars_filter(self):
        self.assertContains(self.res, 's' * 99 + '…')

    def test_redirect_anonymoususer(self):
        self.client.get(reverse('user:logout'))
        res = self.client.get(self.url)
        self.assertFalse(res.wsgi_request.user.is_authenticated)
        self.assertRedirects(res, reverse('user:login') + '?next=' + reverse('user:notification'))


class NotifcationDetailView(BaseTestCase):
    def setUp(self):
        super().setUp()
        Notification.objects.create(user=self.user, message='')
        self.url = reverse('user:notification-details', kwargs={'pk': 1})

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_uesd(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/notification-details.html')

    def test_seen_notification(self):
        res = self.client.get(self.url)
        self.assertContains(res, 'نوتیفیکیشن به حالت دیده شده تغییر یافت.')

    def test_unduplicated_notfication_seen_message(self):
        self.client.get(self.url)
        res = self.client.get(self.url)
        self.assertNotContains(res, 'نوتیفیکیشن به حالت دیده شده تغییر یافت.')

    def test_redirect_anonymous_user(self):
        self.client.get(reverse('user:logout'))
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res ,reverse('user:login') + '?next=' + self.url)


class TestNotifcationDeleteView(BaseTestCase):
    def setUp(self):
        super().setUp()
        Notification.objects.create(user=self.user, message='sss')
        user2 = User.objects.create(username='user2')
        Notification.objects.create(user=user2, message='ssss')
        self.url = reverse('user:notification-delete', kwargs={'pk': 1})
        self.logout_url = reverse('user:logout')
        self.notification_url = reverse('user:notification')

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)

    def test_redirect_after_delete_notification(self):
        notif = Notification.objects.create(user=self.user, message='ssf')
        res = self.client.get(reverse('user:notification-delete', kwargs={'pk': notif.pk}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.notification_url)

    def test_delete_notification(self):
        notif = Notification.objects.create(user=self.user, message='ssf')
        res = self.client.get(reverse('user:notification-delete', kwargs={'pk': notif.pk}))
        self.assertRedirects(res, reverse('user:notification'))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(self.notification_url)
        self.assertEqual(res.context['notification_list'].count(), 1)

    def test_redirect_anonaymous_user(self):
        self.client.get(reverse('user:logout'))
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        notification_count = Notification.objects.all().count()
        self.assertEqual(notification_count, 2)


class TestBookmarkView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('user:user-bookmarks')
        self.poster = SimpleUploadedFile(
            name = 'test.jpg',
            content = b'',
            content_type = 'image/jpeg'
        )
        Movie.objects.create(
            persian_name = 'ss',
            english_name = 'ss',
            year_create = 2022,
            slug = 'sss',
            imdb_point = 2.5,
            baner = self.poster,
        )

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/bookmark.html')

    def test_pagination_template_included(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'components/pagination.html')

    def tearDown(self):
        os.remove('media/images/movies/test.jpg')
