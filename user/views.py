from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login
from .models import User
from .forms import LoginForm


class LoginView(View):

    template_name = 'user/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': LoginForm()})

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request.POST)
        context = {}

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