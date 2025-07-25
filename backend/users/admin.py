from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, UserProfile, UserSettings


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'name', 'surname', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональна інформація', {'fields': ('name', 'surname', 'phone_number')}),
        ('Права доступу', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Додаткове', {'fields': ('role', 'is_verified_email', 'last_login')}),
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
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile

    list_display = ('user', 'location', 'organization', 'specialization', 'education_level')
    list_filter = ('education_level', 'organization')
    search_fields = ('user__email', 'user__name', 'user__surname', 'organization', 'specialization')

    fieldsets = (
        ('Основна інформація', {'fields': ('user', 'profile_picture')}),
        ('Деталі профілю', {'fields': ('location', 'organization', 'specialization', 'education_level')}),
        ('Опис', {'fields': ('bio',)}),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    model = UserSettings

    list_display = ('user', 'email_notifications', 'push_notifications', 'show_profile_to_others')
    list_filter = ('email_notifications', 'push_notifications', 'deadline_reminders')
    search_fields = ('user__email', 'user__name', 'user__surname')

    fieldsets = (
        ('Користувач', {'fields': ('user',)}),
        ('Сповіщення', {'fields': ('email_notifications', 'push_notifications', 'deadline_reminders')}),
        ('Приватність', {'fields': ('show_profile_to_others', 'show_achievements')}),
    )
