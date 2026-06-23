from pathlib import Path

from decouple import config

from team_finder.constants import (
    ALLOWED_HOSTS_DEFAULT,
    DEFAULT_SECRET_KEY,
)
from team_finder.constants import LANGUAGE_CODE as DEFAULT_LANGUAGE_CODE
from team_finder.constants import (
    POSTGRES_DB_DEFAULT,
    POSTGRES_HOST_DEFAULT,
    POSTGRES_PASSWORD_DEFAULT,
    POSTGRES_PORT_DEFAULT,
    POSTGRES_USER_DEFAULT,
    TEMPLATES_DIR,
)
from team_finder.constants import TIME_ZONE as DEFAULT_TIME_ZONE

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default=DEFAULT_SECRET_KEY)

DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default=ALLOWED_HOSTS_DEFAULT,
    cast=lambda value: [host.strip() for host in value.split(",") if host.strip()],
)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "projects.apps.ProjectsConfig",
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

ROOT_URLCONF = "team_finder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / TEMPLATES_DIR],
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

WSGI_APPLICATION = "team_finder.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default=POSTGRES_DB_DEFAULT),
        "USER": config("POSTGRES_USER", default=POSTGRES_USER_DEFAULT),
        "PASSWORD": config("POSTGRES_PASSWORD", default=POSTGRES_PASSWORD_DEFAULT),
        "HOST": config("POSTGRES_HOST", default=POSTGRES_HOST_DEFAULT),
        "PORT": config("POSTGRES_PORT", default=POSTGRES_PORT_DEFAULT, cast=int),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []
if not DEBUG:
    AUTH_PASSWORD_VALIDATORS.extend(
        [
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
    )

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = DEFAULT_LANGUAGE_CODE

TIME_ZONE = DEFAULT_TIME_ZONE

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Media files

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Use custom user model
AUTH_USER_MODEL = "users.User"

# Authentication
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "projects:list"
LOGOUT_REDIRECT_URL = "projects:list"
