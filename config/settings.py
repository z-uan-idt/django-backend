from datetime import datetime, timedelta
from decouple import Csv, config
from pathlib import Path
import os

from config.tasks import TASK_SCHEDULE


DEBUG = config('DEBUG', default=True, cast=bool)

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=[], cast=Csv())

SECRET_KEY = config("SECRET_KEY", default="", cast=str)

INSTALLED_APPS = [
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.extentions",
    "apps.accounts",
    "apps.workspace",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "utils.exception.ExceptionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "utils.middleware.MultiTableAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_currentuser.middleware.ThreadLocalUserMiddleware",
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "utils.exception.ExceptionHandler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["utils.authentication.MultiAuthentication"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

# Security Settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CORS Settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "pharmago",
    },
    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "USER": config("POSTGRES_USER", cast=str),
    #     "HOST": config("POSTGRES_HOST", cast=str),
    #     "PORT": config("POSTGRES_PORT", cast=str),
    #     "NAME": config("POSTGRES_DBNAME", cast=str),
    #     "PASSWORD": config("POSTGRES_PASS", cast=str),
    # }
}

REDIS_HOST = config("REDIS_HOST", default=None, cast=str)

REDIS_PORT = config("REDIS_PORT", default=None, cast=str)

if REDIS_HOST and REDIS_PORT:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "RETRY_ON_TIMEOUT": True,
            },
        }
    }
    
    # Cache timeout settings
    CACHE_TTL = 60 * 15  # 15 minutes
    CACHE_MIDDLEWARE_SECONDS = CACHE_TTL
    
    # Session cache
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = "Asia/Ho_Chi_Minh"
    CELERY_BEAT_SCHEDULE = TASK_SCHEDULE

MONGO_URI = config("MONGO_URI", cast=str, default=None)

if MONGO_URI:
    from pymongo import MongoClient

    MONGO_CLIENT = MongoClient(MONGO_URI)
else:
    MONGO_CLIENT = None

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

TIME_ZONE = "Asia/Ho_Chi_Minh"

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.AdminUser"

# JWT CONFIG
JWT_CONFIG = {
    "ALGORITHM": "HS256",
    "USER_CLAIM": "user_id",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPE": "Bearer",
    "CUSTOMER_CLAIM": "customer_id",
    "AUTH_SYSTEM_NAME": "HTTP_SYSTEM",
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "TOKEN_LIFETIME": timedelta(minutes=config("TOKEN_LIFETIME", cast=int, default=5)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_LIFETIME", cast=int, default=30)),
}

# Swagger
SWAGGER_SETTINGS = {
    "PERSIST_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "authorization",
            "in": "header",
        },
        "System": {
            "type": "apiKey",
            "name": "system",
            "in": "header",
        }
    },
    "USE_SESSION_AUTH": False,
    "FORCE_SCRIPT_NAME": "/",
    "DOC_EXPANSION": "none",
}

# File size
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500 MB

FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

# Backblaze
DEFAULT_FILE_STORAGE = "utils.b2_storage.storage.B2Storage"

BACKBLAZEB2_APP_KEY_ID = config("BACKBLAZEB2_APP_KEY_ID", cast=str, default="")

BACKBLAZEB2_APP_KEY = config("BACKBLAZEB2_APP_KEY", cast=str, default="")

BACKBLAZEB2_BUCKET_NAME = config("BACKBLAZEB2_BUCKET_NAME", cast=str, default="")

BACKBLAZEB2_BUCKET_ID = config("BACKBLAZEB2_BUCKET_ID", cast=str, default="")

BACKBLAZEB2_ACCOUNT_ID = config("BACKBLAZEB2_ACCOUNT_ID", cast=str, default="")

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = config("EMAIL_HOST", cast=str, default="")

EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=str, default="")

EMAIL_PORT = config("EMAIL_PORT", cast=str, default="")

EMAIL_HOST_USER = config("EMAIL_HOST_USER", cast=str, default="")

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", cast=str, default="")

# Logging
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_NAME = datetime.now().strftime("%Y-%m-%d") + ".log"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "()": "utils.logging.VietnameseFormatter",
            "format": "[{asctime}] {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
        "colored": {
            "()": "utils.logging.ColoredFormatter",
            "format": "[{asctime}] {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "filters": {
        "production_filter_logging": {
            "()": "utils.logging.ProductionFilterLogging",
        },
        "debug_filter_logging": {
            "()": "utils.logging.DebugFilterLogging",
        },
        "filter_logging": {
            "()": "utils.logging.FilterLogging",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "filters": ["debug_filter_logging", "filter_logging"],
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "errors-" + LOG_FILE_NAME),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
            "encoding": "utf-8",
            "filters": ["production_filter_logging"],
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.exception": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
