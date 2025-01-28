from unittest.mock import patch
from django_recaptcha.client import RecaptchaResponse
from django.test import TestCase
from .models import User
from django.urls import reverse


class TestLoginView(TestCase):
    def setUp(self):
        user = User.objects.create(username='user', number='09123456789')
        user.set_password('password')
        user.save()

        self.url = reverse('user:login')
        self.data = {
            'username': 'test',
            'password': 'test',
            'g-recaptcha-response': 'mocked-captcha-response'
        }

    def test_url_exist(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/login.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_fail_login_user_not_exist(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        res = self.client.post(self.url, data=self.data)
        self.assertContains(res, 'خطا: نام کاربری یا پسورد نادرست است.')

    def test_failed_login_recaptcha(self):
        del self.data['g-recaptcha-response']
        res = self.client.post(self.url, data=self.data)
        self.assertContains(res, 'لطفا کپچا رو تایید کنید.')

    def test_failed_login_requiered_fields(self):
        res = self.client.post(self.url, data={})
        required_fields = ['username', 'password', 'recaptcha']

        for field in required_fields:
            with self.subTest(field=field):
                self.assertContains(res, 'This field is required.')

    # Error when recaptcha in form is active
    # @patch('django_recaptcha.fields.client.submit')
    # def test_login_success(self, mocked_value):
    #     mocked_value.return_value = RecaptchaResponse(is_valid=True)
    #     data = {
    #         'username': 'user',
    #         'password': 'password',
    #         'g-recaptcha-response': 'mocked-captcha-response'
    #     }

    #     res = self.client.post(self.url, data=data)
    #     print(res.content.decode('utf-8'))
    #     self.assertEqual(User.objects.get(username='user').username, 'user')
    #     self.assertEqual(res.wsgi_request.user.username, 'user')
