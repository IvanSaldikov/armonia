from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from api_keys.forms import GenerateAPIKeyForm
from api_keys.models import APIKey
from users.models import User


class APIKeyListView(LoginRequiredMixin, ListView):
    model = APIKey
    paginate_by = 1  # by default only 1 key allowed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user).order_by("id")


@login_required
def generate_api_key_view(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = GenerateAPIKeyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            new_api_key_form = form.save(commit=False)
            user: User = request.user
            new_api_key_form.user = user
            new_api_key_form.save()
            return HttpResponseRedirect(reverse_lazy('api-keys-list'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = GenerateAPIKeyForm()

    return render(request, "api_keys/apikey_list.html", {"form": form})


class ThankYouView(TemplateView):
    template_name = "chats/thank_you.html"


class PurchaseErrorView(TemplateView):
    template_name = "api_keys/error.html"
