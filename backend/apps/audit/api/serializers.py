from rest_framework import serializers


class AuditEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    actor_username = serializers.CharField(read_only=True)
    action = serializers.CharField(read_only=True)
    target_type = serializers.CharField(read_only=True)
    target_id = serializers.CharField(read_only=True)
    metadata = serializers.DictField(read_only=True)
    request_id = serializers.CharField(read_only=True)


class AuditSearchQuerySerializer(serializers.Serializer):
    action = serializers.CharField(required=False, allow_blank=True)
    target_type = serializers.CharField(required=False, allow_blank=True)
    target_id = serializers.CharField(required=False, allow_blank=True)
