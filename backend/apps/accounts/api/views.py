from contextlib import suppress

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserSummarySerializer,
)


@extend_schema(responses=LoginResponseSerializer)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    throttle_scope = "login"  # limite anti force brute


class RefreshView(TokenRefreshView):
    """Rotation du refresh token : l'ancien est mis en liste noire."""

    throttle_scope = "login"


class LogoutView(APIView):
    permission_classes = [AllowAny]  # le refresh token fait foi

    @extend_schema(request=LogoutSerializer, responses={204: None})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with suppress(TokenError):  # déjà invalide : la déconnexion reste idempotente
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSummarySerializer

    def get_object(self):
        return self.request.user
