import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from notifications.utils.connection_manager import ConnectionManager


class NotificationConnectionsView(LoginRequiredMixin, TemplateView):
    template_name = "user/notification_connections.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["SERVICE_PROVIDERS"] = ConnectionManager.get_active_service_providers()
        return context


@login_required
def confirm_notification_connection(request, uuid_id: uuid.UUID):
    ConnectionManager.confirm_notification_connection_by_uuid(uuid_id=uuid_id,
                                                              user=request.user,
                                                              )
    return HttpResponseRedirect(reverse_lazy('user_notification_connections'))


@login_required
def remove_notification_connection(request, service_provider_name: str):
    ConnectionManager.remove_notification_connection(service_provider_name=service_provider_name,
                                                     user=request.user,
                                                     )
    return HttpResponseRedirect(reverse_lazy('user_notification_connections'))
