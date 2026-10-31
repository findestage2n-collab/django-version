"""Développement local. Ne jamais utiliser en production."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me-0123456789abcdef")

from .base import *  # noqa: E402,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
API_DOCS_ENABLED = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
