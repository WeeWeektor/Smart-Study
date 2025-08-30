from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, activate
from django.conf import settings

from users.models import CustomUser, UserProfile, UserSettings


class LanguageAwareAdminMixin:
    def get_form(self, request, obj=None, **kwargs):
        language = request.COOKIES.get('django_language')
        if language and language in [lang[0] for lang in settings.LANGUAGES]:
            activate(language)
        return super().get_form(request, obj, **kwargs)


@admin.register(CustomUser)
class CustomUserAdmin(LanguageAwareAdminMixin, UserAdmin):
    model = CustomUser

    list_display = ('email', 'name', 'surname', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (gettext('Personal information'), {'fields': ('name', 'surname', 'phone_number')}),
        (gettext('Access rights'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (gettext('Additional'), {'fields': ('role', 'is_verified_email', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'phone_number', 'role', 'password1', 'password2', 'is_staff',
                'is_superuser', 'is_active')}
         ),
    )

    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)


@admin.register(UserProfile)
class UserProfileAdmin(LanguageAwareAdminMixin, admin.ModelAdmin):
    model = UserProfile

    list_display = ('user', 'location', 'organization', 'specialization', 'education_level')
    list_filter = ('education_level', 'organization')
    search_fields = ('user__email', 'user__name', 'user__surname', 'organization', 'specialization')

    fieldsets = (
        (gettext('Basic information'), {'fields': ('user', 'profile_picture')}),
        (gettext('Profile details'), {'fields': ('location', 'organization', 'specialization', 'education_level')}),
        (gettext('Description'), {'fields': ('bio',)}),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(LanguageAwareAdminMixin, admin.ModelAdmin):
    model = UserSettings

    list_display = ('user', 'email_notifications', 'push_notifications', 'show_profile_to_others')
    list_filter = ('email_notifications', 'push_notifications', 'deadline_reminders')
    search_fields = ('user__email', 'user__name', 'user__surname')

    fieldsets = (
        (gettext('User'), {'fields': ('user',)}),
        (gettext('Notification'), {'fields': ('email_notifications', 'push_notifications', 'deadline_reminders')}),
        (gettext('Privacy'), {'fields': ('show_profile_to_others', 'show_achievements')}),
    )
