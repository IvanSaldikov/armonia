from allauth.socialaccount.providers.base import AuthError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet, Count, OuterRef, Subquery
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from chats.models import Message
from problems.forms import ProblemAddNewForm
from problems.models import Problem
from problems.utils import ProblemManager


class ProblemListView(ListView):
    template_name = "problems/list.html"
    model = Problem
    paginate_by = 15
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.is_active_chats():
            qs = self.get_active_chats_queryset()
            qs = self._apply_only_active_chats_filter(qs)
        else:
            if self.is_public():
                qs = self.get_public_queryset()
            else:
                qs = self.get_private_queryset()
        # qs = self._apply_search_strings(qs)
        qs = self._apply_randomize_if_needed(qs)
        return qs

    def _apply_randomize_if_needed(self, qs: QuerySet[Problem]) -> QuerySet[Problem]:
        if self.is_public():
            return qs.order_by("?")
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_public"] = self.is_public()
        context["is_active_chats"] = self.is_active_chats()
        # context = self._apply_search_to_context(context=context)
        # context["form"] = ProblemSearchBox(data=context)
        return context

    def get_public_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_active=True,
                       is_public=True,
                       )
        return qs

    def get_private_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_active=True,
                       author=self.request.user,
                       )
        return qs

    def get_active_chats_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_active=True,
                       )
        return qs

    @staticmethod
    def is_public():
        raise NotImplementedError

    @staticmethod
    def is_active_chats():
        raise NotImplementedError

    def _apply_search_strings(self, qs: QuerySet[Problem]) -> QuerySet[Problem]:
        self._search_age_min = self.request.GET.get("age_min", 18)
        self._search_age_max = self.request.GET.get("age_max", 22)
        if self._search_age_max:
            self._search_age_max = int(self._search_age_max)
            if 18 < self._search_age_max > 60:
                self._search_age_max = 60
            qs = qs.filter(age__lte=self._search_age_max)
        if self._search_age_min:
            self._search_age_min = int(self._search_age_min)
            if 18 < self._search_age_min > 60:
                self._search_age_min = 18
            qs = qs.filter(age__gte=self._search_age_min)
        if self._search_age_min and self._search_age_max and self._search_age_min > self._search_age_max:
            self._search_age_max = self._search_age_min

        return qs

    def _apply_only_active_chats_filter(self, qs: QuerySet[Problem]) -> QuerySet[Problem]:
        messages_obj = Message.objects.order_by("-created_at").filter(room__problem_id=OuterRef("id"), room__user=self.request.user)
        qs = qs.filter(rooms__user=self.request.user
                       ).annotate(messages_count=Count("rooms__messages")
                                  ).filter(messages_count__gt=0
                                           ).annotate(
            latest_message_photo=Subquery(messages_obj.values("photo")[:1]),
            latest_message_text=Subquery(messages_obj.values("message")[:1]),
            latest_message_date=Subquery(messages_obj.values("created_at")[:1])
            ).order_by("-latest_message_date")

        return qs

    def _apply_search_to_context(self, context: dict) -> dict:
        context["age_min"] = self._search_age_min
        context["age_max"] = self._search_age_max
        return context


class ProblemPublicListView(ProblemListView):
    @staticmethod
    def is_public():
        return True

    @staticmethod
    def is_active_chats():
        return False


class ProblemPrivateListView(LoginRequiredMixin, ProblemListView):
    @staticmethod
    def is_public():
        return False

    @staticmethod
    def is_active_chats():
        return False


class ProblemActiveListView(ProblemPrivateListView):

    @staticmethod
    def is_active_chats():
        return True


class ProblemPublicDetailView(DetailView):
    template_name = "problems/detail.html"
    model = Problem

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProblemCreateFormView(LoginRequiredMixin, ListView):
    template_name = "problems/add.html"
    model = Problem

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["form"] = ProblemAddNewForm()
        return context


@login_required
def add_new_problem(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            raise AuthError
        form = ProblemAddNewForm(request.POST)
        if form.is_valid():
            params = form.cleaned_data
            params["author"] = request.user
            new_problem = ProblemManager.create_problem(params=params)
            messages.add_message(request,
                                 messages.SUCCESS,
                                 f"New problem to Solve "
                                 f"has been created successfully. "
                                 "Now you can start chatting",
                                 )
        else:
            return render(request,
                          "problems/add.html",
                          {"form": form,
                           "errors": form.errors,
                           }
                          )
    return HttpResponseRedirect(reverse_lazy('problems-list-private'))
