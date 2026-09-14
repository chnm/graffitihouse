from pathlib import Path

import environ
from django.templatetags.static import static
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
env = environ.FileAwareEnv(
    DEBUG=(bool, False),
)
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-wu9#po37gfc6e$9bg#qt&fqk42+flc8zp^4xj)(=etm@_lg%#8",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]"]
)
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=["http://localhost"]
)

# Application definition
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.import_export",
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    "prose",
    "taggit",
    "taggit_selectize",
    "import_export",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "tailwind",
    "theme",
    "django.contrib.staticfiles",
    "django_extensions",
    "simple_history",
    # apps:
    "graffiti",
    "people",
    "source",
    "accounts",
    "pages",
]

UNFOLD = {
    "SITE_TITLE": "Graffiti House administration",
    "SITE_HEADER": "Graffiti House",
    "SITE_SUBHEADER": "Civil War Graffiti Project",
    "SITE_URL": "/",
    "SITE_SYMBOL": "history_edu",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "6px",
    "DASHBOARD_CALLBACK": "config.admin_dashboard.dashboard_callback",
    "STYLES": [lambda request: static("admin/css/graffitihouse.css")],
    "COMMAND": {
        "search_models": True,
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Wall documentation",
                "separator": True,
                "items": [
                    {
                        "title": "Walls",
                        "icon": "imagesmode",
                        "link": reverse_lazy("admin:graffiti_graffitiwall_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "graffiti.view_graffitiwall"
                        ),
                    },
                    {
                        "title": "Graffiti photos",
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:graffiti_graffitiphoto_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "graffiti.view_graffitiphoto"
                        ),
                    },
                    {
                        "title": "Locations",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:graffiti_location_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "graffiti.view_location"
                        ),
                    },
                    {
                        "title": "Sites",
                        "icon": "museum",
                        "link": reverse_lazy("admin:graffiti_site_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "graffiti.view_site"
                        ),
                    },
                ],
            },
            {
                "title": "Research collections",
                "separator": True,
                "items": [
                    {
                        "title": "Ancillary sources",
                        "icon": "description",
                        "link": reverse_lazy("admin:source_ancillarysource_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "source.view_ancillarysource"
                        ),
                    },
                    {
                        "title": "Archives",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:source_archive_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "source.view_archive"
                        ),
                    },
                ],
            },
            {
                "title": "People and access",
                "separator": True,
                "items": [
                    {
                        "title": "People",
                        "icon": "person",
                        "link": reverse_lazy("admin:people_person_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "people.view_person"
                        ),
                    },
                    {
                        "title": "Users",
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:accounts_customuser_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "accounts.view_customuser"
                        ),
                    },
                    {
                        "title": "Groups",
                        "icon": "group_work",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "auth.view_group"
                        ),
                    },
                ],
            },
        ],
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]


# Development tools
# ------------------------------------------------------------------------------
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar", "django_browser_reload"]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]
    WHITENOISE_USE_FINDERS = True

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

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
ASGI_APPLICATION = "config.asgi.application"
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

database_url = env("DATABASE_URL", default="").strip()
if database_url:
    DATABASES = {"default": env.db_url_config(database_url)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": env("DB_HOST", default="localhost"),
            "PORT": env("DB_PORT", default="5432"),
            "NAME": env("DB_NAME", default="graffitihouse"),
            "USER": env("DB_USER", default="graffitihouse"),
            "PASSWORD": env("DB_PASS", default="password"),
        }
    }

DATABASE_READ_ONLY = env.bool("DATABASE_READ_ONLY", default=False)
allow_migrations = env("DATABASE_ALLOW_MIGRATIONS", default="").strip()
DATABASE_ALLOW_MIGRATIONS = (
    env.bool("DATABASE_ALLOW_MIGRATIONS")
    if allow_migrations
    else not DATABASE_READ_ONLY
)

default_database = DATABASES["default"]
default_database["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
default_database["CONN_HEALTH_CHECKS"] = env.bool("DB_CONN_HEALTH_CHECK", default=True)

if default_database["ENGINE"] == "django.db.backends.postgresql":
    database_options = default_database.setdefault("OPTIONS", {})
    application_name = env("DB_APPLICATION_NAME", default="graffitihouse").strip()
    sslmode = env("DB_SSLMODE", default="").strip()
    sslrootcert = env("DB_SSLROOTCERT", default="").strip()

    if application_name:
        database_options.setdefault("application_name", application_name)
    if sslmode:
        database_options.setdefault("sslmode", sslmode)
    if sslrootcert:
        database_options.setdefault("sslrootcert", sslrootcert)
    if DATABASE_READ_ONLY:
        existing_options = database_options.get("options", "").strip()
        database_options["options"] = " ".join(
            option
            for option in (existing_options, "-c default_transaction_read_only=on")
            if option
        )

AUTH_USER_MODEL = "accounts.CustomUser"

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

TAGGIT_TAGS_FROM_STRING = "taggit_selectize.utils.parse_tags"
TAGGIT_STRING_FROM_TAGS = "taggit_selectize.utils.join_tags"

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
## Tailwind specifics
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = [
    "127.0.0.1",
]
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
