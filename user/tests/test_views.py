from unittest.mock import patch
from django_recaptcha.client import RecaptchaResponse
from django.test import TestCase
from ..models import User
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
    def test_login_success(self, mocked_value):
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

    