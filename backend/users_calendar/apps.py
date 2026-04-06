from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users_calendar'
    verbose_name = _('Users Calendar')
