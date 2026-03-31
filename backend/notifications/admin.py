from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user_email',
        'notification_type',
        'sent_at',
        'is_read',
        'is_important'
    )

    list_filter = (
        'notification_type',
        'is_read',
        'is_important',
        'sent_at'
    )

    search_fields = (
        'title',
        'message',
        'user__email',
        'user__name',
        'user__surname'
    )

    readonly_fields = ('sent_at', 'id')

    fieldsets = (
        (_('Key information'), {
            'fields': ('id', 'user', 'notification_type', 'is_important', 'is_read')
        }),
        (_('Content'), {
            'fields': ('title', 'message', 'sent_at')
        }),
        (_('Links and references'), {
            'fields': ('course', 'event', 'personal_link', 'link_text'),
            'description': _('Select a course or event, or provide an external link.')
        }),
    )

    actions = ['mark_as_read_action', 'mark_as_unread_action']

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = _('User Email')
    user_email.admin_order_field = 'user__email'

    @admin.action(description=_("Mark selected items as read"))
    def mark_as_read_action(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, _("Your selected notifications have been updated."))

    @admin.action(description=_("Mark selected items as unread"))
    def mark_as_unread_action(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, _("The status of the notifications has been changed to 'unread'."))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course', 'event')
