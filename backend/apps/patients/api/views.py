"""Couche HTTP : valider la forme de l'entrée, vérifier les droits, appeler UN cas d'usage.

Aucune règle métier ici, et aucun import de l'infrastructure (le câblage est dans composition.py).
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.patients.composition import build_patient_use_cases
from apps.patients.domain.repositories import PatientSearch
from core.interface.actors import actor_from_request
from core.interface.pagination import DefaultPagination
from core.interface.permissions import HasActionPermission

from .serializers import (
    PatientDetailSerializer,
    PatientListSerializer,
    PatientSearchQuerySerializer,
    PatientWriteSerializer,
)

PUBLIC_ID = OpenApiParameter("public_id", OpenApiTypes.UUID, OpenApiParameter.PATH)


@extend_schema_view(
    list=extend_schema(
        parameters=[PatientSearchQuerySerializer], responses=PatientListSerializer(many=True)
    ),
    retrieve=extend_schema(parameters=[PUBLIC_ID], responses=PatientDetailSerializer),
    create=extend_schema(request=PatientWriteSerializer, responses={201: PatientDetailSerializer}),
    partial_update=extend_schema(
        parameters=[PUBLIC_ID], request=PatientWriteSerializer, responses=PatientDetailSerializer
    ),
    destroy=extend_schema(parameters=[PUBLIC_ID], responses={204: None}),
)
class PatientViewSet(viewsets.GenericViewSet):
    permission_classes = [HasActionPermission]
    permission_map = {
        "list": "patients.view_patient",
        "retrieve": "patients.view_patient",
        "create": "patients.add_patient",
        "partial_update": "patients.change_patient",
        "destroy": "patients.delete_patient",
    }
    pagination_class = DefaultPagination
    filter_backends: list = []
    serializer_class = PatientDetailSerializer
    lookup_field = "public_id"
    lookup_value_regex = "[0-9a-fA-F-]{36}"
    use_cases = staticmethod(build_patient_use_cases)  # remplaçable dans les tests

    def list(self, request):
        query = PatientSearchQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        results = self.use_cases().search.execute(PatientSearch(**query.to_criteria_kwargs()))
        page = self.paginate_queryset(results)
        return self.get_paginated_response(PatientListSerializer(page, many=True).data)

    def retrieve(self, request, public_id=None):
        return Response(PatientDetailSerializer(self.use_cases().get.execute(public_id)).data)

    def create(self, request):
        serializer = PatientWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        allow_duplicate = data.pop("allow_duplicate", False)
        patient = self.use_cases().register.execute(
            data=data, actor=actor_from_request(request), allow_duplicate=allow_duplicate
        )
        return Response(PatientDetailSerializer(patient).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, public_id=None):
        serializer = PatientWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        data.pop("allow_duplicate", None)
        patient = self.use_cases().update.execute(
            public_id=public_id, changes=data, actor=actor_from_request(request)
        )
        return Response(PatientDetailSerializer(patient).data)

    def destroy(self, request, public_id=None):
        self.use_cases().archive.execute(public_id=public_id, actor=actor_from_request(request))
        return Response(status=status.HTTP_204_NO_CONTENT)
