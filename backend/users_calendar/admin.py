from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import BaseUserCalendar, PersonalEvent, CourseCalendarEvent


@admin.register(BaseUserCalendar)
class BaseUserCalendarAdmin(admin.ModelAdmin):
    list_display = ('user', 'id')
    search_fields = ('user__email', 'user__username')
    ordering = ('user',)


@admin.register(PersonalEvent)
class PersonalEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_user', 'event_date', 'importance', 'is_completed', 'created_at')
    list_filter = ('importance', 'is_completed', 'event_date', 'calendar__user')
    search_fields = ('title', 'description', 'calendar__user__email')
    fieldsets = (
        (_('Main Information'), {
            'fields': ('calendar', 'title', 'description', 'importance')
        }),
        (_('Date & Status'), {
            'fields': ('event_date', 'is_completed', 'completed_at')
        }),
        (_('Additional Details'), {
            'fields': ('link', 'id'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('id', 'created_at', 'updated_at', 'completed_at')

    def get_user(self, obj):
        return obj.calendar.user.email

    get_user.short_description = _('User')


@admin.register(CourseCalendarEvent)
class CourseCalendarEventAdmin(admin.ModelAdmin):
    list_display = ('course', 'get_content_type', 'get_user', 'event_date', 'is_completed')
    list_filter = ('course', 'is_completed', 'event_date', 'calendar__user')
    search_fields = ('course__title', 'note', 'calendar__user__email', 'lesson__title')

    raw_id_fields = (
        'course', 'module', 'lesson', 'module_test', 'course_test'
    )

    fieldsets = (
        (_('Links'), {
            'fields': ('calendar', 'course', 'module', 'lesson', 'module_test', 'course_test')
        }),
        (_('Event Details'), {
            'fields': ('event_date', 'note', 'link', 'is_completed')
        }),
        (_('System'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('id', 'created_at', 'updated_at')

    def get_user(self, obj):
        return obj.calendar.user.email

    get_user.short_description = _('User')

    def get_content_type(self, obj):
        if obj.lesson: return f"📖 {obj.lesson.title}"
        if obj.module_test: return f"📝 Test: {obj.module_test.title}"
        if obj.course_test: return f"🏆 Final: {obj.course_test.title}"
        return "---"

    get_content_type.short_description = _('Content')
