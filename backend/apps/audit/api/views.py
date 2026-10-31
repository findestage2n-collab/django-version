from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.response import Response

from apps.audit.composition import build_get_audit_entry, build_search_audit_entries
from apps.audit.domain.repositories import AuditSearch
from core.interface.pagination import DefaultPagination
from core.interface.permissions import HasActionPermission

from .serializers import AuditEntrySerializer, AuditSearchQuerySerializer

ENTRY_ID = OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH)


@extend_schema_view(
    list=extend_schema(parameters=[AuditSearchQuerySerializer]),
    retrieve=extend_schema(parameters=[ENTRY_ID]),
)
class AuditLogViewSet(viewsets.GenericViewSet):
    """Consultation du journal (rôle ADMIN). Lecture seule."""

    permission_classes = [HasActionPermission]
    permission_map = {"list": "audit.view_auditlog", "retrieve": "audit.view_auditlog"}
    serializer_class = AuditEntrySerializer
    pagination_class = DefaultPagination
    filter_backends: list = []
    lookup_value_regex = "[0-9]+"
    search_use_case = staticmethod(build_search_audit_entries)
    get_use_case = staticmethod(build_get_audit_entry)

    def list(self, request):
        query = AuditSearchQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        results = self.search_use_case().execute(AuditSearch(**query.validated_data))
        page = self.paginate_queryset(results)
        return self.get_paginated_response(AuditEntrySerializer(page, many=True).data)

    def retrieve(self, request, pk=None):
        entry = self.get_use_case().execute(int(pk))
        return Response(AuditEntrySerializer(entry).data)
