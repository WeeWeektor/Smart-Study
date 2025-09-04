from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser, UserProfile, UserSettings


@admin.action(description=_('Позначити як активні'))
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'name', 'surname', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name', 'surname')
    list_per_page = 25
    ordering = ('email',)
    readonly_fields = ('last_login', 'is_verified_email')
    actions = [make_active]

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


class BaseUserRelatedAdmin(admin.ModelAdmin):
    """Базовий клас для моделей пов'язаних з користувачем"""

    list_per_page = 25
    search_fields_for_user = ('user__email', 'user__name', 'user__surname')
    ordering_for_user = ('user__email',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')

    def get_user_display(self, obj):
        return f"{obj.user.name} {obj.user.surname}"

    get_user_display.short_description = _('Користувач')

    def get_user_email(self, obj):
        return obj.user.email

    get_user_email.short_description = _('Електронна пошта')


@admin.register(UserProfile)
class UserProfileAdmin(BaseUserRelatedAdmin):
    model = UserProfile
    list_select_related = ('user',)
    raw_id_fields = ('user',)

    list_display = ('get_user_display', 'get_user_email', 'location', 'organization', 'specialization', 'education_level')
    list_filter = ('education_level', 'user__is_active', 'user__role')
    search_fields = BaseUserRelatedAdmin.search_fields_for_user
    ordering = BaseUserRelatedAdmin.ordering_for_user
    list_per_page = BaseUserRelatedAdmin.list_per_page

    fieldsets = (
        (_('Basic information'), {'fields': ('user', 'profile_picture')}),
        (_('Profile details'), {'fields': ('location', 'organization', 'specialization', 'education_level')}),
        (_('Description'), {'fields': ('bio',)}),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(BaseUserRelatedAdmin):
    model = UserSettings
    list_select_related = ('user',)
    raw_id_fields = ('user',)

    list_display = ('get_user_display', 'get_user_email', 'email_notifications', 'push_notifications', 'show_profile_to_others')
    list_filter = ('show_profile_to_others', 'show_achievements', 'user__is_active', 'user__role')
    search_fields = BaseUserRelatedAdmin.search_fields_for_user
    ordering = BaseUserRelatedAdmin.ordering_for_user
    list_per_page = BaseUserRelatedAdmin.list_per_page

    fieldsets = (
        (_('Basic information'), {'fields': ('user',)}),
        (_('Notification'), {'fields': ('email_notifications', 'push_notifications', 'deadline_reminders')}),
        (_('Privacy'), {'fields': ('show_profile_to_others', 'show_achievements')}),
    )
