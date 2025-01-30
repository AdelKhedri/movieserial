from django.test import TestCase
from ..models import User
from django_recaptcha.client import RecaptchaResponse
from unittest.mock import patch
from ..forms import RegisterForm


class TestLoginView(TestCase):
    def setUp(self):
        user = User.objects.create(username='user', email='user@gmail.com')
        user.set_password('pass')
        user.save()

    def test_required_fields(self):
        form = RegisterForm(data={})
        fields = ['username', 'email', 'number', 'accept_rules', 'password1', 'password2']

        self.assertFalse(form.is_valid())
        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(form.errors[field][0], 'این فیلد لازم است.')

    def test_username_duplicate(self):
        data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password1': 'pass1234', 
            'password2': 'pass1234',
            'accept_rules': True
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], 'نام کاربری تکراری است.')

    def test_username_duplicate(self):
        data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password1': 'pass1234', 
            'password2': 'pass1234',
            'accept_rules': True
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], 'نام کاربری تکراری است.')

    def test_email_duplicate(self):
        data = {
            'username': 'users',
            'email': 'user@gmail.com',
            'password1': 'pass1234', 
            'password2': 'pass1234',
            'accept_rules': True
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'ایمیل تکراری است.')

    def test_not_match_passwords(self):
        data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'number': '09123456789',
            'password1': 'pass1234', 
            'password2': 'pass123s4',
            'accept_rules': True
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0], 'پسورد ها با هم مطابقت ندارند.')

    def test_form_valid(self):
        data = {
            'username': 'users',
            'email': 'usesr@gmail.com',
            'number': '09123456789',
            'password1': 'pass1234', 
            'password2': 'pass1234',
            'accept_rules': True
        }
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
