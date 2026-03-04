from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env()

environ.Env.read_env(env.str("DOTENV_PATH", ".env"))

VERSION = env("VERSION", default="1")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


INSTALLED_APPS = [
    # UNFOLD
    "unfold",
    # DJANGO
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # APPS
    "base",
    "account",
    "habit",
    "analytics",
    # REST
    "rest_framework",
    "rest_framework_json_api",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_json_api.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_METADATA_CLASS": "rest_framework_json_api.metadata.JSONAPIMetadata",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        "rest_framework_json_api.django_filters.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
    "SEARCH_PARAM": "filter[search]",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "vnd.api+json",
    # "DEFAULT_AUTHENTICATION_CLASSES": [
    #     # "apps.account.services.auth.authentication.CustomUserAuthentication", TODO: Использовать при получении токена через админку  # noqa: E501
    #     "rest_framework.authentication.SessionAuthentication",
    # ],
    # "DEFAULT_PERMISSION_CLASSES": [
    #     "apps.account.api_v1.permissions.IsCustomUserPermission",
    #     # "rest_framework.permissions.AllowAny",
    # ],
}

JSON_API_FORMAT_FIELD_NAMES = "camelize"
JSON_API_FORMAT_TYPES = "camelize"

SPECTACULAR_SETTINGS = {
    "TITLE": "HABIT API",
    "DESCRIPTION": "Автодокументация дневника привычек",
    "VERSION": VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    # "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.SessionAuthentication"],
    "SCHEMA_PATH_PREFIX": "/api-v1",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
}

JWT_ACCESS_TOKEN_LIFETIME = timedelta(hours=env.float("ACCESS_TOKEN_LIFETIME", 1))
JWT_REFRESH_TOKEN_LIFETIME = timedelta(hours=env.float("REFRESH_TOKEN_LIFETIME", 48))
JWT_SIGNING_KEY = env.str("SIGNING_KEY", "test")
JWT_ALGORITHM = "HS256"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.str("REDIS_PORT", 6379)
REDIS_URL = env.str("REDIS_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}")
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=f"{REDIS_URL}/0")
CELERY_RESULT_URL = env.str("CELERY_RESULT_URL", default=f"{REDIS_URL}/0")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465

EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Clickhouse
CLICKHOUSE_HOST = env.str("CLICKHOUSE_HOST", default="localhost")
CLICKHOUSE_PORT = env.str("CLICKHOUSE_PORT", default="8123")
CLICKHOUSE_DATABASE = env.str("CLICKHOUSE_DATABASE", default="habit_tracker")
CLICKHOUSE_USER = env.str("CLICKHOUSE_USER", default="default")
CLICKHOUSE_PASSWORD = env.str("CLICKHOUSE_PASSWORD")

# Kafka
KAFKA_BOOTSTRAP_SERVERS = env.list("KAFKA_BOOTSTRAP_SERVERS", default=["localhost:9092"])
KAFKA_AUTO_OFFSET_RESET = env.str("KAFKA_AUTO_OFFSET_RESET", default="earliest")
KAFKA_ENABLE_AUTO_COMMIT = env.bool("KAFKA_ENABLE_AUTO_COMMIT", default=False)

AUTH_USER_MODEL = "account.CustomUser"

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


LANGUAGE_CODE = "ru-ru"
TIME_ZONE = TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

UNFOLD = {
    "SITE_TITLE": "Habit Tracker Admin",
    "SITE_HEADER": "Админ-панель",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
        },
    },
}
