from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate, login
from .models import User, ForgotPasswordLink
from .forms import LoginForm, RegisterForm, RecaptchaForm, ChangePasswordForgotPasswordFrom
from django.http import HttpResponse
from django.conf import settings
from random import randint
from .otp import OtpCode
from datetime import timedelta
from django.utils import timezone


class LoginView(View):

    template_name = 'user/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': LoginForm(), 'page_name': 'ورود'})

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request.POST)
        context = {'page_name': 'ورود'}

        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, username = username, password = password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', None)
                return redirect(next_url if next_url else '/admin/login/')
            else:
                context['msg'] = 'failed to authenticate.'
        context['form'] = login_form
        return render(request, self.template_name, context)


class RegisterView(View):
    template_name = 'user/register.html'

    def get(self, request, *args, **kwargs):
        context = {
            'recaptcha_form': RecaptchaForm(),
            'register_form': RegisterForm(),
            'page_name': 'ثبت نام',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {
            'recaptcha_form': RecaptchaForm(),
            'register_form': RegisterForm(),
            'page_name': 'ثبت نام',
        }
        recaptcha_form = RecaptchaForm(request.POST)

        if recaptcha_form.is_valid():
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                number = register_form.cleaned_data['number']
                code = randint(123456,987989)
                otp = OtpCode(request, number, code)
                otp.save()
                # print(code)
                return redirect('user:confirm-number')

                # TODO: Send code and redirect to confirm user
            else:
                context['register_form'] = register_form
        context['recaptcha_form'] = recaptcha_form
        return render(request, self.template_name, context)


class ConfirmNumberView(View):
    template_name = 'user/confirm.html'

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('number', None) is None:
                return redirect('user:register')
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'page_name': 'تایید شماره'})

    def post(self, request, *args, **kwargs):
        context = {'page_name': 'تایید شماره'}

        code = request.POST.get('code', None)
        if code:
            otp = OtpCode(request)
            if otp.validate_code(int(code)):
                user = User.objects.get(number=otp.number)
                user.is_active = True
                user.save()
                login(request, user)
                next_url = request.GET.get('next', None)
                return redirect(next_url if next_url else settings.LOGIN_REDIRECT_URL)
            else:
                context['msg'] = 'کد معتبر نیست.'
        else:
            context['msg'] = 'لطفا کد زا وارد کنید.'
        return render(request, self.template_name, context)


class ForgotPasswordView(View):
    template_name = 'user/forgot-password.html'

    def get(self, request, *args, **kwargs):
        context = {
            'page_title': 'فراموشی رمز عبور | نت موی',
            'page_name': 'فراموشی رمز عبور',
            'recaptcha_form': RecaptchaForm(),
            }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'page_name': 'فراموشی رمز عبور'}
        recaptcha_form = RecaptchaForm(request.POST)
        if recaptcha_form.is_valid():
            number = request.POST.get('number', None)
            users = User.objects.filter(number=number)

            if users.exists():
                links = ForgotPasswordLink.objects.filter(user=users.first())
                if links.exists():
                    if links.filter(time__gte = timezone.now()).exists():
                        context['msg'] = 'please wait'
                    else:
                        links.first().delete()
                        ForgotPasswordLink.objects.create(user=users.first(), time = timezone.now() + timedelta(minutes=5))
                        # TODO: send forgot_password_inc.link to number
                        context['msg'] = 'link sended'
                else:
                    ForgotPasswordLink.objects.create(user=users.first(), time = timezone.now() + timedelta(minutes=5))
                    # TODO: send forgot_password_inc.link to number
                    context['msg'] = 'link sended'
            else:
                context['msg'] = 'number not found'
        else:
            context.update({
                'recaptcha_form': recaptcha_form,
                'msg': 'captcha failed',
                })
        return render(request, self.template_name, context)


class ForgotPasswordChangePasswordView(View):
    template_name = 'user/forgot-password.html'

    def dispatch(self, request, link, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        self.context = {
            'page_title': 'تنظیم پسورد جدید | نت موی',
            'page_name': 'تنظیم رمز عبور جدید',
            'change_password': ChangePasswordForgotPasswordFrom(),
            'recaptcha_form': RecaptchaForm(),
            }
        return super().dispatch(request, link, *args, **kwargs)

    def get(self, request, link, *args, **kwargs):
        get_object_or_404(ForgotPasswordLink, link=link)
        return render(request, self.template_name, self.context)

    def post(self, request, link, *args, **kwargs):
        recaptcha_form = RecaptchaForm(request.POST)
        if recaptcha_form.is_valid():
            forgot_password_link = get_object_or_404(ForgotPasswordLink, link=link)
            change_password_form = ChangePasswordForgotPasswordFrom(request.POST)
            if change_password_form.is_valid():
                user = forgot_password_link.user
                password = change_password_form.cleaned_data.get('password1')
                user.set_password(password)
                user.save()
                forgot_password_link.delete()
                self.context['msg'] = 'change password successful'
            else:
                self.context['change_password'] = change_password_form
        else:
            self.context['msg'] = 'invalid captcha'
        return render(request, self.template_name, self.context)


def home(request):
    return HttpResponse(f'{request.user}')
