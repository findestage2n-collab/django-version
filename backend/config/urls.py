from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.infrastructure.health import liveness, readiness

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("health/", liveness, name="health-live"),
    path("health/ready/", readiness, name="health-ready"),
    # API versionnée : web ET mobile consomment /api/v1/
    path("api/v1/", include("config.api_v1")),
]

if settings.API_DOCS_ENABLED:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    ]
