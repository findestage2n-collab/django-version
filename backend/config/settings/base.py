"""Réglages communs à tous les environnements (aucun secret en dur)."""

from contextlib import suppress
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
PROJECT_DIR = BASE_DIR.parent

env = environ.Env()
_env_file = PROJECT_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file, overwrite=False)

# ── Sécurité de base ────────────────────────────────────────────────
SECRET_KEY = env("DJANGO_SECRET_KEY")  # obligatoire : pas de valeur par défaut
DEBUG = env.bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")  # à changer en production

# ── Applications ────────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",  # Swagger UI embarqué : la doc API fonctionne SANS Internet
]
LOCAL_APPS = [
    "core",
    # Modules métier (monolithe modulaire) - voir docs/01-architecture.md
    "apps.accounts",
    "apps.audit",
    "apps.personnel",
    "apps.patients",
    "apps.rendezvous",
    "apps.consultations",
    "apps.hospitalisations",
    "apps.laboratoire",
    "apps.pharmacie",
    "apps.facturation",
    "apps.paiements",
    "apps.rapports",
    "apps.notifications",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Modèle utilisateur personnalisé : à définir AVANT la première migration.
AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sert les fichiers statiques sans nginx ni CDN
    "corsheaders.middleware.CorsMiddleware",
    "core.infrastructure.middleware.RequestIdMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

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
            ]
        },
    }
]

# ── Bases relationnelles : SQLite, MySQL 8.4 ou PostgreSQL ─────────
DATABASES = {"default": env.db("DATABASE_URL")}
if DATABASES["default"]["ENGINE"].endswith("mysql"):
    DATABASES["default"].setdefault("OPTIONS", {}).update(
        {"charset": "utf8mb4", "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"}
    )
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", 60)
# Transactions explicites dans les services (transaction.atomic), pas ATOMIC_REQUESTS.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Mots de passe ───────────────────────────────────────────────────
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internationalisation ────────────────────────────────────────────
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True  # stockage en UTC ; l'API renvoie de l'ISO 8601

# ── Fichiers statiques / médias (sur disque : aucun stockage cloud requis) ──
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
with suppress(OSError):  # évite l'avertissement de WhiteNoise avant le premier collectstatic
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Cache ───────────────────────────────────────────────────────────
# Aucun service externe (ni Redis, ni Celery) : le système fonctionne sur un seul serveur,
# sans Internet. Les événements sont traités en mémoire (core/infrastructure/events.py).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ── E-mail : jamais d'envoi vers Internet par défaut ────────────────
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.filebased.EmailBackend")
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

# ── Django REST Framework : contrat commun web + mobile ─────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "core.interface.pagination.DefaultPagination",
    "DEFAULT_FILTER_BACKENDS": [],  # filtres = critères du domaine, pas de filtres sur QuerySet
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("THROTTLE_ANON", default="30/min"),
        "user": env("THROTTLE_USER", default="600/min"),
        "login": env("THROTTLE_LOGIN", default="10/min"),
    },
    "EXCEPTION_HANDLER": "core.interface.exceptions.api_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DATETIME_FORMAT": "iso-8601",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES", 15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", 7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Hospital Management API",
    "DESCRIPTION": "API REST du frontend web (Vue.js) et de l'application mobile (Flutter).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "COMPONENT_SPLIT_REQUEST": True,
    # Ressources de la page /api/docs/ servies localement (pas de CDN)
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
API_DOCS_ENABLED = env.bool("API_DOCS_ENABLED", False)

# ── CORS (le mobile n'est pas concerné ; seul le web l'est) ─────────
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_EXPOSE_HEADERS = ["X-Request-ID"]

# ── Journalisation : un identifiant de requête dans chaque ligne ────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "core.infrastructure.logging.RequestIdFilter"}},
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "standard",
        }
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
