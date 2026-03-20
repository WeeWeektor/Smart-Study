from rest_framework import serializers

from .models import BaseUserCalendar, PersonalEvent, CourseCalendarEvent


class PersonalEventSerializer(serializers.ModelSerializer):
    is_personal = serializers.ReadOnlyField(default=True)
    event_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=True)

    class Meta:
        model = PersonalEvent
        fields = [
            'id', 'title', 'description', 'event_date',
            'importance', 'link', 'is_completed',
            'completed_at', 'is_personal'
        ]
        read_only_fields = ['id', 'completed_at']

    def create(self, validated_data):
        user = self.context.get('user')
        if not user:
            user = self.context['request'].user

        calendar, _ = BaseUserCalendar.objects.get_or_create(user=user)
        validated_data['calendar'] = calendar
        return super().create(validated_data)


class CourseCalendarEventSerializer(serializers.ModelSerializer):
    is_personal = serializers.ReadOnlyField(default=False)
    course_title = serializers.CharField(source='course.title', read_only=True)
    event_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    class Meta:
        model = CourseCalendarEvent
        fields = [
            'id', 'course', 'course_title', 'event_date',
            'note', 'is_personal'
        ]
        read_only_fields = ['id']


class UserCalendarSummarySerializer(serializers.ModelSerializer):
    personal_events = PersonalEventSerializer(many=True, read_only=True)
    course_events = CourseCalendarEventSerializer(many=True, read_only=True)

    class Meta:
        model = BaseUserCalendar
        fields = ['personal_events', 'course_events']
