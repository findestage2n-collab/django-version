"""Production : HTTPS, cookies sécurisés, base relationnelle configurable. Fonctionne HORS LIGNE (LAN)."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False

SUPPORTED_DATABASE_ENGINES = {
    "django.db.backends.mysql",
    "django.db.backends.postgresql",
    "django.db.backends.sqlite3",
}
if DATABASES["default"]["ENGINE"] not in SUPPORTED_DATABASE_ENGINES:  # noqa: F405
    raise ImproperlyConfigured(
        "Moteur de base non pris en charge. Utilisez MySQL, PostgreSQL ou SQLite "
        "avec le DATABASE_URL correspondant."
    )
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS est obligatoire en production.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", True)  # noqa: F405
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

# Fichiers statiques compressés et versionnés, servis par WhiteNoise (aucun CDN)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Cache partagé entre les processus gunicorn, sans Redis : fichiers locaux
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": env("CACHE_DIR", default=str(BASE_DIR / ".cache")),  # noqa: F405
    }
}
