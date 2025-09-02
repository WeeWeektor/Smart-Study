from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser, UserProfile, UserSettings


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'name', 'surname', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal information'), {'fields': ('name', 'surname', 'phone_number')}),
        (_('Access rights'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Additional'), {'fields': ('role', 'is_verified_email', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'phone_number', 'role', 'password1', 'password2',
                'is_staff', 'is_superuser', 'is_active'
            )}
         ),
    )

    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile

    list_display = ('user', 'location', 'organization', 'specialization', 'education_level')
    list_filter = ('education_level', 'organization')
    search_fields = ('user__email', 'user__name', 'user__surname', 'organization', 'specialization')

    fieldsets = (
        (_('Basic information'), {'fields': ('user', 'profile_picture')}),
        (_('Profile details'), {'fields': ('location', 'organization', 'specialization', 'education_level')}),
        (_('Description'), {'fields': ('bio',)}),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    model = UserSettings

    list_display = ('user', 'email_notifications', 'push_notifications', 'show_profile_to_others')
    list_filter = ('email_notifications', 'push_notifications', 'deadline_reminders')
    search_fields = ('user__email', 'user__name', 'user__surname')

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Notification'), {'fields': ('email_notifications', 'push_notifications', 'deadline_reminders')}),
        (_('Privacy'), {'fields': ('show_profile_to_others', 'show_achievements')}),
    )
