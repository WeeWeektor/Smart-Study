from rest_framework import serializers

from courses.models import Module, Lesson, Test
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

    module_id = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(), source='module', required=False, allow_null=True
    )
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(), source='lesson', required=False, allow_null=True
    )
    module_test_id = serializers.PrimaryKeyRelatedField(
        queryset=Test.objects.all(), source='module_test', required=False, allow_null=True
    )
    course_test_id = serializers.PrimaryKeyRelatedField(
        queryset=Test.objects.all(), source='course_test', required=False, allow_null=True
    )

    class Meta:
        model = CourseCalendarEvent
        fields = [
            'id', 'course', 'course_title', 'module_id', 'lesson_id',
            'module_test_id', 'course_test_id', 'event_date',
            'note', 'link', 'is_completed', 'is_personal'
        ]
        read_only_fields = ['id']


class UserCalendarSummarySerializer(serializers.ModelSerializer):
    personal_events = PersonalEventSerializer(many=True, read_only=True)
    course_events = CourseCalendarEventSerializer(many=True, read_only=True)

    class Meta:
        model = BaseUserCalendar
        fields = ['personal_events', 'course_events']
