from django.views.generic import TemplateView

from problems.utils import ProblemManager


class MainView(TemplateView):
    template_name = "main/main.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = ProblemManager.get_default_problem()
        context["default_problem"] = problem
        return context


class PricingView(TemplateView):
    template_name = "main/pricing.html"


class PurchasingView(TemplateView):
    template_name = "main/purchasing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_purchasing"] = True
        return context


class ContactUsView(TemplateView):
    template_name = "main/contact_us.html"


class TermsOfUseView(TemplateView):
    template_name = "main/terms.html"


class PrivacyPolicyView(TemplateView):
    template_name = "main/privacy.html"


class AboutUsView(TemplateView):
    template_name = "main/about.html"
