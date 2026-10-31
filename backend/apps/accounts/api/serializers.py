from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSummarySerializer(serializers.Serializer):
    """Profil renvoyé au client : le frontend (web/mobile) en déduit les droits d'affichage.

    Les permissions sont informatives : le serveur reste l'autorité sur chaque endpoint.
    """

    public_id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    telephone = serializers.CharField(read_only=True)
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_roles(self, user) -> list[str]:
        return sorted(user.groups.values_list("name", flat=True))

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_permissions(self, user) -> list[str]:
        return sorted(user.get_all_permissions())


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSummarySerializer(self.user).data
        return data


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSummarySerializer()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
