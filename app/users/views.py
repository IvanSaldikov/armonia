from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from countries.utils import CountriesUtils
from users.forms.preferences import UserChooseCountryForm, UserEmailNotificationForm


class UserCountryView(LoginRequiredMixin, TemplateView):
    template_name = "user/country.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserChooseCountryForm(instance=self.request.user)
        return context


@login_required
def save_user_country_view(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = UserChooseCountryForm(data=request.POST, instance=request.user)
        # check whether it's valid:
        if form.is_valid():
            new_value = form.cleaned_data.get("country_code", CountriesUtils.DEFAULT_COUNTRY)
            if new_value.lower() == "id":
                msg = f"The service is not available for this country. Please set up another one"
                messages.add_message(request,
                                     messages.ERROR,
                                     msg,
                                     )
                return HttpResponseRedirect(reverse_lazy('user_country'))
            form.save()
            CountriesUtils.set_lang_into_session(request=request,
                                                 value=new_value,
                                                 )
            msg = f"The country has been changed"
            messages.add_message(request,
                                 messages.SUCCESS,
                                 msg,
                                 )
            return HttpResponseRedirect(reverse_lazy('user_country'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserChooseCountryForm(instance=request.user)
    return render(request, "user/country.html", {"form": form})


class UserEmailNotificationView(LoginRequiredMixin, TemplateView):
    template_name = "user/email_notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserEmailNotificationForm(instance=self.request.user)
        return context


@login_required
def enable_disable_email_notifications(request):
    if request.method == "POST":
        form = UserEmailNotificationForm(data=request.POST,
                                         instance=request.user
                                         )
        if form.is_valid():
            form.save()
            if form.cleaned_data.get("is_email_messages_allowed"):
                msg = f"You've allowed Email notifications from this website!"
            else:
                msg = f"You've disallowed email notifications from this website!"
            messages.add_message(request,
                                 messages.SUCCESS,
                                 msg,
                                 )
            return HttpResponseRedirect(reverse_lazy('problems-list-public'))
    return HttpResponseRedirect(reverse_lazy('user_email_messages'))
