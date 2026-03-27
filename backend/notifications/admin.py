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
        (_('Основна інформація'), {
            'fields': ('id', 'user', 'notification_type', 'is_important', 'is_read')
        }),
        (_('Контент'), {
            'fields': ('title', 'message', 'sent_at')
        }),
        (_('Зв’язки та посилання'), {
            'fields': ('course', 'event', 'personal_link', 'link_text'),
            'description': _('Виберіть об’єкт курсу або події, або вкажіть зовнішнє посилання.')
        }),
    )

    actions = ['mark_as_read_action', 'mark_as_unread_action']

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = _('User Email')
    user_email.admin_order_field = 'user__email'

    @admin.action(description=_("Позначити вибрані як прочитані"))
    def mark_as_read_action(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, _("Вибрані сповіщення оновлено."))

    @admin.action(description=_("Позначити вибрані як НЕпрочитані"))
    def mark_as_unread_action(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, _("Статус сповіщень змінено на 'непрочитано'."))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course', 'event')
