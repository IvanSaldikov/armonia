import logging
import os
import sys
from datetime import timedelta
from pathlib import Path
from typing import List, Tuple

import environ
from django.urls import reverse_lazy

from common.consts import FilesStorage

# https://github.com/joke2k/django-environ
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SILENCED_SYSTEM_CHECKS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("ARMONIA_SECRET_KEY", cast=str)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("ARMONIA_DEBUG", default=False, cast=bool)
TESTING = env("TESTING", default="test" in sys.argv)
DEBUG_TOOLBAR = env("ARMONIA_DEBUG_TOOLBAR", cast=bool, default=True) and not TESTING

STAGE = env("ARMONIA_STAGE", default="dev", cast=str)
# Are we on prod?
IS_PROD = STAGE == "prod"

ALLOWED_HOSTS = env(
    "ARMONIA_DJANGO_ALLOWED_HOSTS",
    default="localhost",
    ).split(" ")

# Application definition

INSTALLED_APPS = [
    "daphne",
    "admin_interface",
    "colorfield",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",  # REMOVED because of recommendations
    "django.contrib.postgres",
    "django.forms",
    "django_countries",

    # Bootstrap Template
    "django_bootstrap5",
    "bootstrap_pagination",

    # 3rd parties
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
    "django_components",
    # "django_components.safer_staticfiles",

    # "dj_rest_auth",
    "drf_spectacular",
    "django.contrib.sites",
    "import_export",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # "allauth.socialaccount.providers.facebook",
    # "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.google",

    # Django Social Share
    # https://pypi.org/project/django-social-share/
    "django_social_share",

    # Google Recaptcha - https://pypi.org/project/django-recaptcha/
    "django_recaptcha",

    # Easy Thumbnais
    "easy_thumbnails",

    # Apps
    "users",
    "main",
    "admin_dashboard",
    "countries",
    "api_keys",
    "notifications",
    "problems",
    "chats",
    "emails",
    ]

# Django Admin Interface
# https://pypi.org/project/django-admin-interface/
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS.append("security.W019")

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "countries.middleware.CountryMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

if DEBUG and DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]


    def show_toolbar(request):
        return DEBUG


    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        }

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates",
                 os.path.join(BASE_DIR, "admin_dashboard/templates/"),
                 ],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.my_settings",
                ],
            'loaders': [(
                'django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django_components.template_loader.Loader',
                    ]
                )],
            'builtins': [
                'django_components.templatetags.component_tags',
                ]
            },
        },
    ]
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'
STATICFILES_DIRS = [
    BASE_DIR / "components",
    ]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# DJANGO REST FRAMEWORK SETTINGS
PAGE_SIZE_LIMIT = env.int("ARMONIA_PAGE_SIZE_LIMIT", 15)
MAX_PAGE_SIZE_LIMIT = env.int("ARMONIA_MAX_PAGE_SIZE_LIMIT", 150)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # "api.permissions.APIKeyPermission",
        ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "config.pagination.ExtendedLimitOffsetPagination",
    "PAGE_SIZE": PAGE_SIZE_LIMIT,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        ],
    }

DEFAULT_THROTTLE_RATES_FOR_ANON_PER_DAY = env.int(
    "ARMONIA_DEFAULT_THROTTLE_RATES_FOR_ANON", 9999
    )
DEFAULT_THROTTLE_RATES_FOR_AUTH_USER_PER_MINUTE = env.int(
    "ARMONIA_DEFAULT_THROTTLE_RATES_FOR_AUTH_USER_PER_MINUTE", 9999
    )
DRF_THROTTLE_SETTINGS = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": f"{DEFAULT_THROTTLE_RATES_FOR_ANON_PER_DAY}/min",
        "user": f"{DEFAULT_THROTTLE_RATES_FOR_AUTH_USER_PER_MINUTE}/min",
        },
    }
if not DEBUG:
    REST_FRAMEWORK.update(DRF_THROTTLE_SETTINGS)
if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "rest_framework.renderers.BrowsableAPIRenderer"
        )

ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

REDIS_CREDS = env("ARMONIA_REDIS_CREDS", default="")
if not REDIS_CREDS.startswith(":"):
    REDIS_CREDS = f":{REDIS_CREDS}"

REDIS_PORT = env("ARMONIA_REDIS_PORT", default=6379, cast=int)
REDIS_HOST = env("ARMONIA_REDIS_HOST", default=f"redis:{str(REDIS_PORT)}/0")
REDIS_URL = f"redis://{REDIS_CREDS}@{REDIS_HOST}"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env("ARMONIA_SQL_ENGINE", default="django.db.backends.sqlite3", cast=str),
        "NAME": env(
            "ARMONIA_SQL_DATABASE", default=os.path.join(BASE_DIR, "db.sqlite3"), cast=str
            ),
        "USER": env("ARMONIA_SQL_USER", default="user", cast=str),
        "PASSWORD": env("ARMONIA_SQL_PASSWORD", default="password", cast=str),
        "HOST": env("ARMONIA_SQL_HOST", default="localhost", cast=str),
        "PORT": env("ARMONIA_SQL_PORT", default="5432", cast=str),
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("ARMONIA_CACHE_LOCATION", default=REDIS_URL),
        }
    }

# CHANNELS
CHANNELS_LOCATION = env("CHANNELS_LOCATION", default=REDIS_URL)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [CHANNELS_LOCATION],
            "capacity": 100,  # default 100
            "expiry": 60,  # default 60
            },
        },
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

default_token_lifetime_minutes = 60 * 24
if DEBUG:
    default_token_lifetime_minutes = 99999
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=default_token_lifetime_minutes),
    "REFRESH_TOKEN_LIFETIME": timedelta(weeks=3),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "JTI_CLAIM": "jti",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(weeks=3),
    }

# CORS
CORS_ALLOW_HEADERS = [
    "Access-Control-Allow-Origin",
    "Access-Control-Allow-Credentials",
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    ]
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    ]

CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    # https://github.com/adamchainz/django-cors-headers#cors_allow_credentials-bool
    SESSION_COOKIE_SAMESITE = None

CORS_ALLOW_ALL_ORIGINS = DEBUG
default_frontend_localhost = "http://localhost:3000"
CORS_ALLOWED_ORIGINS = env(
    "ARMONIA_CORS_ALLOWED_ORIGINS",
    default=default_frontend_localhost,
    ).split(" ")
if DEBUG:
    if default_frontend_localhost not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(default_frontend_localhost)
CSRF_COOKIE_SECURE = not DEBUG
CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS

# Social Auth (Dj-REST-Auth)
GOOGLE_REDIRECT_URL = "http://localhost:8000"
SITE_ID = 1
REST_USE_JWT = True
if not DEBUG:
    # User Cookies for authentication
    JWT_AUTH_COOKIE = "auth-token"
else:
    JWT_AUTH_COOKIE = None
JWT_AUTH_REFRESH_COOKIE = "refresh-token"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
USER_MODEL_EMAIL_FIELD = "email"
USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False  # Whether send email if no user has been found
SOCIAL_LOGIN_CALLBACK_URL_GOOGLE = env(
    "ARMONIA_SOCIAL_LOGIN_CALLBACK_URL_GOOGLE",
    default="http://localhost:8000/api/rest-auth/google/",
    )
# When changing password force to enter the old one
REST_AUTH_SERIALIZERS = {
    #    "PASSWORD_RESET_SERIALIZER": "users.serializers.PasswordResetSerializerExt",
    # "LOGIN_SERIALIZER": "custom_jwt.serializers.LoginSerializerWithoutUserName",
    # "USER_DETAILS_SERIALIZER": "custom_jwt.serializers.UserDetailsWithoutPkSerializer",
    }
OLD_PASSWORD_FIELD_ENABLED = True
SOCIALACCOUNT_AUTO_SIGNUP = False
ACCOUNT_EMAIL_VERIFICATION = "none"
# ACCOUNT_ADAPTER = "custom_jwt.views.CustomAccountAdapter"
# REST_AUTH_REGISTER_SERIALIZERS = {
#     "REGISTER_SERIALIZER": "custom_jwt.serializers.RegistrationSerializerWithoutUserName"
# }
REST_AUTH_PW_RESET_USE_SITES_DOMAIN = True
# REST_AUTH_TOKEN_MODEL = "custom_jwt.tokens.JWTAccessToken"
IS_REGISTRATION_ON = True

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# if USE_L10N is set to True, then the locale-dictated format has higher precedence and will be applied instead
# https://stackoverflow.com/questions/7216764/in-the-django-admin-site-how-do-i-change-the-display-format-of-time-fields
USE_L10N = True

from django.conf.locale.en import formats as en_formats
from django.conf.locale.ru import formats as ru_formats

en_formats.DATETIME_FORMAT = "Y-m-d H:i:s"
ru_formats.DATETIME_FORMAT = "Y-m-d H:i:s"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_DOMAIN_NAME = "https://armonia.day"
CSRF_TRUSTED_ORIGINS = [
    "https://*.armonia.day",
    ]

EMAIL_BACKEND = env(
    "ARMONIA_EMAIL_BACKEND",
    # Send Emails to the console by default
    default="django.core.mail.backends.console.EmailBackend",
    )
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "i@armonia.day"
EMAIL_HOST_PASSWORD = env("ARMONIA_EMAIL_HOST_PASSWORD", default=None)
# AWS Throttle port 25, see:
# https://aws.amazon.com/fr/premiumsupport/knowledge-center/ec2-port-25-throttle/
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_FROM = "i@armonia.day"

# Email used for regular email messages
DEFAULT_FROM_EMAIL = "Armonia.day <i@armonia.day>"

ADMINS = (("Admin", "your_email@mail.com"),)
if not str(STAGE).lower().startswith("prod"):
    ADMINS = []

# SENDGRID
# Sendgrid service for email sending: https://app.sendgrid.com/login
# https://pypi.org/project/django-sendgrid-v5/
SENDGRID_API_KEY = env("ARMONIA_SENDGRID_API_KEY", default=None)
SENDGRID_SANDBOX_MODE_IN_DEBUG = env(
    "ARMONIA_SENDGRID_SANDBOX_MODE_IN_DEBUG", cast=bool, default=False
    )
# These are needed to make links in emails readable and not changed by Sendgrid
SENDGRID_TRACK_EMAIL_OPENS = False
SENDGRID_TRACK_CLICKS_PLAIN = False

ENCRYPT_PASSWORD = env(
    "ARMONIA_ENCRYPT_PASSWORD", default="1111111111111111111111111111111111"
    )

# Celery config
broker_url = env("ARMONIA_CEL_BROKER_URL", default=REDIS_URL)
celery_backend_url = env("ARMONIA_CEL_BACKEND_URL", default=REDIS_URL)
BROKER_URL = env("ARMONIA_CEL_BROKER_URL", default=REDIS_URL)
CELERY_BACKEND_URL = env("ARMONIA_CEL_BACKEND_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = 'redis://%s:%d/2' % (REDIS_HOST, REDIS_PORT)
CELERY_BROKER_URL = env("ARMONIA_CEL_BACKEND_URL", default=REDIS_URL)
CELERY_ROUTES = {
    'problems.tasks.generate_avatar_for_problem': {'queue': 'avatars'},
    'chats.tasks.generate_problem_image_and_send_back_to_user': {'queue': 'photos'},
    'chats.tasks.process_user_input': {'queue': 'chats'},
    'admin_dashboard.tasks.save_metrics_to_db': {'queue': 'other'},
    }
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_DEFAULT_QUEUE = 'other'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"
task_always_eager = False
beat_schedule_filename = env("CELERY_BEAT_SCHEDULE_FILENAME",
                             default="/home/app/web/celerybeat-schedule",
                             cast=str,
                             )

# SENTRY
SENTRY_DSN = env("ARMONIA_SENTRY_DSN", default=None, cast=str)
SENTRY_DISABLED_ENVS = ("dev",)
if SENTRY_DSN and IS_PROD:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=STAGE,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.01,
        profiles_sample_rate=0.01,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        )

SPECTACULAR_SETTINGS = {
    "TITLE": "Armonia.day API",
    "DESCRIPTION": "Armonia.day API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    }

# ADMIN URL PROTECTION
# Admin url protection from accidentally accessing
# from the Internet by entering /admin/ in the address bar of a web-browser
ADMIN_URL_RND_STRING = env("ARMONIA_ADMIN_URL_RND_STRING", default="/very_long_string_to_admin_panel_5555555555559999999999999")
# Not needed for debug-mode
if DEBUG:
    ADMIN_URL_RND_STRING = ""

# Files Storages
# For prod we need to use another root path (from nginx conf)
MEDIA_ROOT = env("ARMONIA_MEDIA_ROOT", default="/mnt/media", cast=str)
MEDIA_URL = "media/"
CURRENT_FILES_STORAGE = env(
    "CURRENT_FILES_STORAGE", default=FilesStorage.FILES.value, cast=str
    )
STORAGES = {
    FilesStorage.MINIO.value: {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    FilesStorage.GOOGLE.value: {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage"
        },
    FilesStorage.FILES.value: {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
        },
    }
GS_IS_GZIPPED = True
STORAGES.update({"default": STORAGES.get(CURRENT_FILES_STORAGE)})

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "assets/"
STATIC_ROOT = env("ARMONIA_STATIC_ROOT", default="/mnt/static", cast=str)
STORAGES.update(
    {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            }
        }
    )

# DJANGO ALLAUTH
# For Django-Allauth this is needed to include:
# https://django-allauth.readthedocs.io/en/latest/installation.html
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    ]
# Allauth forms (можно здесь переопределить формы для авторизации и регистрации)
ACCOUNT_FORMS = {
    'login': 'users.forms.login.TunedLoginForm',
    'signup': 'users.forms.signup.TunedSignupForm',
    'add_email': 'allauth.account.forms.AddEmailForm',
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'set_password': 'allauth.account.forms.SetPasswordForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    }
SOCIALACCOUNT_FORMS = {
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    'signup': 'users.forms.signup.TunedSocialSignupForm',
    }
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True  # Обязательно нужен email
ACCOUNT_USERNAME_REQUIRED = False  # Выключаем ввод имени пользователя
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Доступ по email-у?
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_MAX_EMAIL_ADDRESSES = 1  # Максимальное количество email-ов
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False
# if DEBUG:
#     # Нужно ли верифицировать email, чтобы залогинется
ACCOUNT_EMAIL_VERIFICATION = "none"
# Пути перенаправления при логине и логауте
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = reverse_lazy('account_signup')
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_USERNAME_BLACKLIST = ["admin",
                              "administrator",
                              "moderator",
                              ]  # имена которые нельзя использовать при регистрации
ACCOUNT_USERNAME_MIN_LENGTH = 4  # минимальное число символов при регистрации
# Social login:
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_EMAIL_REQUIRED = ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_STORE_TOKENS = False
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/en/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v9.0',
        },
    'google': {
        'SCOPE': [
            'profile',
            'email',
            ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            }
        }
    }

# Google Captcha
# https://pypi.org/project/django-recaptcha/
from django_recaptcha.constants import TEST_PUBLIC_KEY, TEST_PRIVATE_KEY

RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default=TEST_PUBLIC_KEY, cast=str)
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default=TEST_PRIVATE_KEY, cast=str)
if DEBUG:
    SILENCED_SYSTEM_CHECKS.append("django_recaptcha.recaptcha_test_key_error")

# Bootstrap 5 Library
# https://django-bootstrap5.readthedocs.io/en/stable/settings.html
BOOTSTRAP5 = {
    # The complete URL to the Bootstrap CSS file.
    # Note that a URL can be either a string
    # ("https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css"),
    # or a dict with keys `url`, `integrity` and `crossorigin` like the default value below.
    "css_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
        # "integrity": "sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN",
        "crossorigin": "anonymous",
        },
    "javascript_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js",
        "integrity": "sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM",
        "crossorigin": "anonymous",
        },
    'wrapper_class': 'mb-5 form-el',
    'field_renderers': {
        'default': 'common.forms.CustomFieldRenderer',
        },
    }

# COUNTRIES
from django.utils.translation import gettext_lazy as _

ARMONIA_GEO_DATA_FILE_LOCATION = env("ARMONIA_GEO_DATA_FILE_LOCATION",
                                     default="/mnt/geo_data/country.mmdb",
                                     cast=str,
                                     )
# COUNTRIES_OVERRIDE = {
#     "CD": _("Congo"),
#     "HM": _("Head Island"),
#     "FM": _("Micronesia"),
#     "SH": _("Saint Helena"),
#     "GS": _("South Georgia"),
#     "UM": _("US Minor Outlying Islands"),
#     }

# EASY THUMBNAILS
# https://pypi.org/project/easy-thumbnails/
THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (300, 400), 'crop': True},
        },
    }
