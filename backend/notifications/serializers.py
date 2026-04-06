from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='annotated_source_name', read_only=True)

    internal_url = serializers.ReadOnlyField()
    external_url = serializers.ReadOnlyField()
    action_text = serializers.ReadOnlyField()
    sent_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'is_read',
            'is_important',
            'title',
            'message',
            'sent_at',
            'source_name',
            'internal_url',
            'external_url',
            'action_text',
        ]
        read_only_fields = ['id', 'sent_at', 'notification_type']

    @staticmethod
    def get_source_name(obj):
        """Повертає назву курсу або заголовку події залежно від того, що заповнено"""
        if obj.course:
            return obj.course.title
        if obj.event:
            return obj.event.title
        return None


class NotificationMarkReadSerializer(serializers.Serializer):
    """Спеціальний серіалізатор для масового оновлення статусу прочитання"""
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True
    )
