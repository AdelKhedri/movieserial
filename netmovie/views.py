from django.shortcuts import render
from django.views.generic import ListView, View
from cinema.models import MainPageCarousel, MainPageCategory, Country, Geners
from .forms import ContactUsForm
from user.forms import RecaptchaForm


class Home(ListView):
    template_name = 'cinema/index.html'
    queryset = MainPageCategory.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carousel_list'] = MainPageCarousel.objects.all()
        context['gener_list'] = Geners.objects.all()
        context['country_list'] = Country.objects.all()
        context['home'] = 'active'
        return context


class ContactUsView(View):
    template_name = 'cinema/contact-us.html'

    def setup(self, request, *args, **kwargs):
        self.context = {
            'form': ContactUsForm(),
            'gener_list': Geners.objects.all(),
            'country_list': Country.objects.all(),
            'recaptcha_form': RecaptchaForm(),
            'contact_us': 'active'
        }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        recaptcha_form = RecaptchaForm(request.POST)
        if recaptcha_form.is_valid():
            form_contact_us = ContactUsForm(request.POST)
            if form_contact_us.is_valid():
                form_contact_us.save()
                self.context['msg'] = 'success full'
            else:
                self.context['form'] = form_contact_us
        else:
            self.context['msg'] = 'recaptcha failed'
        return render(request, self.template_name, self.context)


def termsView(request):
    context = {
        'gener_list': Geners.objects.all(),
        'country_list': Country.objects.all(),
    }
    return render(request, 'cinema/terms.html', context)


