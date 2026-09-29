from importlib.util import find_spec
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

# Production runs behind a proxy (Caddy) that terminates HTTPS and sets
# X-Forwarded-Proto. Trusting it makes absolute URLs, such as the API's links,
# use https. Only enable this when every request comes through such a proxy.
if env.bool("DJANGO_BEHIND_HTTPS_PROXY", default=True):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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
    "django.contrib.staticfiles",
    "simple_history",
    "allauth",
    "allauth.account",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
    # apps:
    "graffiti",
    "people",
    "source",
    "accounts",
    "pages",
    "api",
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
                        "title": "Team",
                        "icon": "groups",
                        "link": reverse_lazy("admin:pages_teammember_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "pages.view_teammember"
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
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]


# Development tools
# ------------------------------------------------------------------------------
# Dev tools live in the `dev` dependency group, which the production image
# does not install, so only enable them when they are actually importable.
DEV_TOOLS = DEBUG and find_spec("debug_toolbar") is not None
if DEV_TOOLS:
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
            # Leave DB_PASS unset to let libpq read ~/.pgpass (or PGPASSFILE).
            "PASSWORD": env("DB_PASS", default=""),
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

# Authentication (django-allauth)
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_ADAPTER = "accounts.adapter.InviteOnlyAccountAdapter"
ACCOUNT_LOGIN_METHODS = {"email", "username"}
# Signup is closed (see adapter); password1 here keeps the password field on the login form.
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*"]
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_LOGIN_BY_CODE_SUPPORTS_RESEND = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGOUT_ON_GET = False
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/"

# Email. Login codes and password resets go through this backend.
# Examples: consolemail:// (default, prints to the terminal),
# smtp+tls://user:pass@smtp.example.org:587
_email = env.email_url_config(env("EMAIL_URL", default="").strip() or "consolemail://")
_email_options = {
    "EMAIL_HOST": "host",
    "EMAIL_PORT": "port",
    "EMAIL_HOST_USER": "username",
    "EMAIL_HOST_PASSWORD": "password",
    "EMAIL_USE_TLS": "use_tls",
    "EMAIL_USE_SSL": "use_ssl",
    "EMAIL_FILE_PATH": "file_path",
}
MAILERS = {
    "default": {
        "BACKEND": _email["EMAIL_BACKEND"],
        "OPTIONS": {
            name: _email[key]
            for key, name in _email_options.items()
            if _email.get(key) not in ("", None)
        },
    }
}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="graffitihouse@localhost")

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

# Public API (Django REST Framework)
# ------------------------------------------------------------------------------
# The API at /api/v1/ is public and read-only. Authentication is switched off so
# every caller, staff included, gets the same anonymous, throttled responses.
num_proxies = env("API_NUM_PROXIES", default="").strip()
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.StandardPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    # A DRF rate such as 120/minute or 5000/day. Counts live in the default
    # cache, which is per process unless CACHES points at a shared backend.
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("API_THROTTLE_RATE", default="120/minute"),
    },
    # Trusted reverse proxies in front of the app, so throttling keys on the
    # client address in X-Forwarded-For rather than the proxy's. Blank = unset.
    "NUM_PROXIES": int(num_proxies) if num_proxies else None,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Latitude and longitude as JSON numbers rather than strings.
    "COERCE_DECIMAL_TO_STRING": False,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Civil War Graffiti Project API",
    "DESCRIPTION": (
        "Public, read-only data from the Civil War Graffiti Project: sites, "
        "locations, walls, graffiti photos, and people. `description` fields on "
        "walls and photos are sanitized HTML."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    # Serve Swagger UI from our own static files instead of a third-party CDN.
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

# CORS: let visualizations hosted elsewhere read the API. Limited to /api/ and
# to safe methods, never with credentials. Leave API_CORS_ALLOWED_ORIGINS blank
# to allow any origin, or list origins to restrict it.
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_METHODS = ["GET", "HEAD", "OPTIONS"]
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOWED_ORIGINS = env.list("API_CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = not CORS_ALLOWED_ORIGINS

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
INTERNAL_IPS = [
    "127.0.0.1",
]
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
