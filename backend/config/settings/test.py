"""Tests : SQLite en mémoire par défaut, ou TEST_DATABASE_URL (MySQL/PostgreSQL en CI)."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-key-not-for-production-0123456789")
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite://:memory:")

from .base import *  # noqa: E402,F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
API_DOCS_ENABLED = True
LOGGING["root"]["level"] = "WARNING"  # noqa: F405
REST_FRAMEWORK = {  # noqa: F405
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {"anon": "10000/min", "user": "10000/min", "login": "10000/min"},
}
MEDIA_ROOT = BASE_DIR / ".test_media"  # noqa: F405
