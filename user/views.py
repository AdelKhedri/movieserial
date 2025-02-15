from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from cinema.models import Country, Geners, MediaBookmark
from .models import HistoryOfSubscription, Package, Profile, User, ForgotPasswordLink, Notification
from .forms import (LoginForm, ProfileUpdateForm, RegisterForm, RecaptchaForm, ChangePasswordForgotPasswordFrom, UserForm,
                    ChangePasswordForm)
from django.conf import settings
from random import randint
from .otp import OtpCode
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, DetailView


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
                return redirect(next_url if next_url else settings.LOGIN_REDIRECT_URL)
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


class DashboardView(LoginRequiredMixin, View):
    template_name = 'user/profile.html'

    def setup(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            Profile.objects.get_or_create(user=request.user)
            self.context = {
                'profile_form': ProfileUpdateForm(instance=request.user.profile),
                'user_form': UserForm(instance=request.user),
                'user': request.user,
                'notification_counts': Notification.objects.filter(user=request.user, status='new').count(),
                'bookmark_count': MediaBookmark.objects.filter(user=request.user).count(),
                'now': timezone.now(),
                'last_subscription': HistoryOfSubscription.objects.filter(user=request.user).last()
            }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        profile_ins = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        user_ins = UserForm(request.POST, instance=request.user)

        if profile_ins.has_changed():
            if profile_ins.is_valid():
                profile_ins.save()
                self.context['profile_form_msg'] = 'profile update success'
            self.context['profile_form'] = profile_ins

        if user_ins.has_changed():
            if user_ins.is_valid():
                user_ins.save()
                request.user.refresh_from_db()
                self.context['user'] = request.user
                self.context['user_form_msg'] = 'user update success'
            self.context['user_form'] = user_ins
        return render(request, self.template_name, self.context)


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'user/change-password.html'

    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.context = {
            'change_password_form': ChangePasswordForm(),
            'notification_counts': Notification.objects.filter(user=request.user, status='new').count(),
            'bookmark_count': MediaBookmark.objects.filter(user=request.user).count(),
            'now': timezone.now(),
            'last_subscription': HistoryOfSubscription.objects.filter(user=request.user).last()
        }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        change_password_form = ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            last_password = change_password_form.cleaned_data['last_password']
            user = authenticate(request, username=request.user.username, password=last_password)
            if user is not None:
                change_password_form.save(user=user)
                self.context['msg'] = 'change_password success'
                login(request, user)
            else:
                change_password_form.add_error('last_password', 'پسورد قبلی اشتباه است.')
        self.context['change_password_form'] = change_password_form
        return render(request, self.template_name, self.context)


class NotificationView(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'user/notification.html'
    context_object_name = 'notification_list'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notification_counts'] = self.get_queryset().filter(status='new').count()
        context['now']= timezone.now()
        context['last_subscription']= HistoryOfSubscription.objects.filter(user=self.request.user).last()
        context['bookmark_count'] = MediaBookmark.objects.filter(user=self.request.user).count()
        return context


class NotificationDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'user/notification-details.html'
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, pk=self.kwargs[self.pk_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookmark_count'] = MediaBookmark.objects.filter(user=self.request.user).count()
        context['now'] = timezone.now()
        context['last_subscription'] = HistoryOfSubscription.objects.filter(user=self.request.user).last()
        notif = self.get_queryset().first()
        if notif.status == 'new':
            notif.status = 'read'
            notif.save()
            context['msg'] = 'notification was seen'
        return context


class NotificationDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notif = get_object_or_404(Notification, user=request.user, pk=kwargs['pk'])
        notif.delete()
        return redirect(reverse('user:notification'))


class BookmarkView(LoginRequiredMixin, ListView):
    template_name = 'user/bookmark.html'
    paginate_by = 15
    context_object_name = 'media_list'
    
    def get_queryset(self):
        return MediaBookmark.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            'bookmark_count': MediaBookmark.objects.filter(user=self.request.user).count(),
            'now': timezone.now(),
            'last_subscription': HistoryOfSubscription.objects.filter(user=self.request.user).last()
        })
        return context


class SubscriptionView(LoginRequiredMixin, View):
    template_name = 'user/subscription.html'

    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.context = {
                'gener_list': Geners.objects.all(),
                'country_list': Country.objects.all(),
                'package_list': Package.objects.all(),
                'bookmark_count': MediaBookmark.objects.filter(user=request.user).count(),
                'subscription': 'active',
                'now': timezone.now(),
            }
        if request.user.special_time:
            self.context['last_subscription'] = HistoryOfSubscription.objects.filter(user=request.user).last()
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('package', None)
        if pk:
            package = get_object_or_404(Package, id=pk)
            user = request.user
            time = timedelta(days=package.days)

            if user.balance >= package.get_final_price():
                if user.special_time is None or user.special_time < timezone.now():
                    user.special_time = timezone.now() + time
                else:
                    user.special_time += time
                user.balance -= package.get_final_price()
                user.save()
                HistoryOfSubscription.objects.create(user=request.user, package = package, payed = True, final_price = package.get_final_price(), days=package.days)
                self.context['msg'] = 'success'
            else:
                self.context['msg'] = 'failed'
        return render(request, self.template_name, self.context)


def logoutView(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('user:login')
