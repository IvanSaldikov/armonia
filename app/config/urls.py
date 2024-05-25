from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
    )

from api_keys.views import ThankYouView
from main.views import PricingView, ContactUsView, AboutUsView, TermsOfUseView, PrivacyPolicyView, \
    PurchasingView
from notifications.views import NotificationConnectionsView, confirm_notification_connection, remove_notification_connection
from problems.views import ProblemPublicListView, ProblemPublicDetailView, add_new_problem, ProblemCreateFormView, ProblemPrivateListView, ProblemActiveListView
from users.views import UserCountryView, save_user_country_view, UserEmailNotificationView, enable_disable_email_notifications


urlpatterns = [
    path(f"admin{settings.ADMIN_URL_RND_STRING}/", admin.site.urls),
    path("admin_dashboard/", include("admin_dashboard.urls")),
    path("pricing/", PricingView.as_view(), name="pricing"),
    path("purchasing/", PurchasingView.as_view(), name="purchasing"),
    path("thank_you/", ThankYouView.as_view(), name="thank-you"),
    path("contact_us/", ContactUsView.as_view(), name="contact-us"),
    path("terms_of_use/", TermsOfUseView.as_view(), name="terms"),
    path("privacy_policy/", PrivacyPolicyView.as_view(), name="privacy"),
    path("about/", AboutUsView.as_view(), name="about"),
    path("user/country", UserCountryView.as_view(), name="user_country"),
    path("user/country/save", save_user_country_view, name="save_user_country"),
    path("user/email_messages_preferences", UserEmailNotificationView.as_view(), name="user_email_messages"),
    path("user/email_messages_preferences_enable_disable", enable_disable_email_notifications, name="email_messages_preferences_enable_disable"),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    path("chats/", include('chats.urls')),
    path("api/", include("api.urls")),

    # API Keys
    # path("api_keys/", APIKeyListView.as_view(), name="api-keys-list"),
    # path("api_keys/add", generate_api_key_view, name="api-keys-add"),
    # path("api_keys/error", PurchaseErrorView.as_view(), name="purchase-error"),

    # Notifications
    path("user/notification_connections", NotificationConnectionsView.as_view(),
         name="user_notification_connections"
         ),
    path("user/notification_connections/confirm/<uuid:uuid_id>",
         confirm_notification_connection, name="confirm_notification_connection"
         ),
    path("user/notification_connections/disconnect/<str:service_provider_name>",
         remove_notification_connection, name="remove_notification_connection"
         ),

    # Problems to Solve
    path("", ProblemPublicListView.as_view(), name="problems-list-public"),
    path("problems_to_solve/private", ProblemPrivateListView.as_view(), name="problems-list-private"),
    path("problems_to_solve/private/active", ProblemActiveListView.as_view(), name="problems-list-private-active"),
    path("problems_to_solve/add_new", ProblemCreateFormView.as_view(), name="problems-add-new-form"),
    path("problems_to_solve/add_new/run", add_new_problem, name="problems-add-new-run"),
    path("problems_to_solve/<slug:slug>", ProblemPublicDetailView.as_view(), name="problems-detail-public"),

    ]

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        ]

urlpatterns += [
    # yaml OpenAPI file generator
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
        ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
        ),
    ]

# https://docs.djangoproject.com/en/4.2/howto/static-files/#serving-files-uploaded-by-a-user-during-development
# Works only for DEBUG=True
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
