from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils.translation import get_language, activate

from smartStudy_backend import settings
from users.admin import CustomUserAdmin, UserProfileAdmin, UserSettingsAdmin
from users.models import CustomUser, UserProfile, UserSettings


class DummyRequest:
    def __init__(self, cookies=None):
        self.COOKIES = cookies or {}


class LanguageAwareAdminMixinTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin_custom_user = CustomUserAdmin(CustomUser, self.site)
        self.admin_user_profile = UserProfileAdmin(UserProfile, self.site)
        self.admin_user_settings = UserSettingsAdmin(UserSettings, self.site)

    def _test_fallback(self, admin_instance):
        request = DummyRequest(cookies={})
        initial_lang = get_language()
        admin_instance.get_form(request)
        self.assertEqual(get_language(), settings.LANGUAGE_CODE.lower())
        activate(initial_lang)

    def _test_fallback_invalid_cookie(self, admin_instance):
        request = DummyRequest(cookies={'django_language': 'xx'})
        initial_lang = get_language()
        admin_instance.get_form(request)
        self.assertEqual(get_language(), settings.LANGUAGE_CODE.lower())
        activate(initial_lang)

    def test_fallback_default_language_custom_user(self):
        self._test_fallback(self.admin_custom_user)

    def test_fallback_default_language_user_profile(self):
        self._test_fallback(self.admin_user_profile)

    def test_fallback_default_language_user_settings(self):
        self._test_fallback(self.admin_user_settings)

    def test_fallback_invalid_cookie_custom_user(self):
        self._test_fallback_invalid_cookie(self.admin_custom_user)

    def test_fallback_invalid_cookie_user_profile(self):
        self._test_fallback_invalid_cookie(self.admin_user_profile)

    def test_fallback_invalid_cookie_user_settings(self):
        self._test_fallback_invalid_cookie(self.admin_user_settings)


class CustomUserAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(CustomUser, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ('email', 'name', 'surname', 'role', 'is_active', 'is_staff')
        )

    def test_list_filter(self):
        self.assertEqual(
            self.admin.list_filter,
            ('role', 'is_active', 'is_staff', 'is_superuser')
        )

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ('email', 'name', 'surname'))

    def test_fieldsets_defined(self):
        self.assertTrue(hasattr(self.admin, 'fieldsets'))
        self.assertTrue(len(self.admin.fieldsets) > 0)

    def test_add_fieldsets_defined(self):
        self.assertTrue(hasattr(self.admin, 'add_fieldsets'))
        self.assertTrue(len(self.admin.add_fieldsets) > 0)


class UserProfileAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserProfileAdmin(UserProfile, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ('get_user_display', 'get_user_email', 'location', 'organization', 'specialization', 'education_level')
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ('education_level', 'user__is_active', 'user__role'))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ('user__email', 'user__name', 'user__surname')
        )

    def test_fieldsets_defined(self):
        self.assertTrue(hasattr(self.admin, 'fieldsets'))
        self.assertTrue(len(self.admin.fieldsets) > 0)

    def test_base_admin_inheritance(self):
        """Тест наслідування від BaseUserRelatedAdmin"""
        from users.admin import BaseUserRelatedAdmin
        self.assertTrue(issubclass(UserProfileAdmin, BaseUserRelatedAdmin))

    def test_raw_id_fields(self):
        """Тест налаштування raw_id_fields"""
        self.assertEqual(self.admin.raw_id_fields, ('user',))

    def test_list_select_related(self):
        """Тест оптимізації запитів"""
        self.assertEqual(self.admin.list_select_related, ('user',))


class UserSettingsAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserSettingsAdmin(UserSettings, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            (
                'get_user_display', 'get_user_email', 'email_notifications', 'push_notifications',
                'show_profile_to_others')
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter,
                         ('show_profile_to_others', 'show_achievements', 'user__is_active', 'user__role'))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ('user__email', 'user__name', 'user__surname')
        )

    def test_fieldsets_defined(self):
        self.assertTrue(hasattr(self.admin, 'fieldsets'))
        self.assertTrue(len(self.admin.fieldsets) > 0)

    def test_notification_fields_in_fieldsets(self):
        """Тест наявності полів уведомлень у fieldsets"""
        notification_fields = None
        for name, options in self.admin.fieldsets:
            if 'email_notifications' in options.get('fields', []):
                notification_fields = options['fields']
                break

        self.assertIsNotNone(notification_fields)
        self.assertIn('email_notifications', notification_fields)
        self.assertIn('push_notifications', notification_fields)
        self.assertIn('deadline_reminders', notification_fields)

    def test_privacy_fields_in_fieldsets(self):
        """Тест наявності полів приватності у fieldsets"""
        privacy_fields = None
        for name, options in self.admin.fieldsets:
            if 'show_profile_to_others' in options.get('fields', []):
                privacy_fields = options['fields']
                break

        self.assertIsNotNone(privacy_fields)
        self.assertIn('show_profile_to_others', privacy_fields)
        self.assertIn('show_achievements', privacy_fields)


class BaseUserRelatedAdminTest(TestCase):
    """Тести для BaseUserRelatedAdmin"""

    def setUp(self):
        self.site = AdminSite()
        self.admin = UserProfileAdmin(UserProfile, self.site)

    def test_get_user_display_method(self):
        """Тест методу get_user_display"""
        self.assertTrue(hasattr(self.admin, 'get_user_display'))
        self.assertTrue(callable(getattr(self.admin, 'get_user_display')))

    def test_get_user_email_method(self):
        """Тест методу get_user_email"""
        self.assertTrue(hasattr(self.admin, 'get_user_email'))
        self.assertTrue(callable(getattr(self.admin, 'get_user_email')))

    def test_search_fields_for_user(self):
        """Тест search_fields для користувача"""
        expected = ('user__email', 'user__name', 'user__surname')
        self.assertEqual(self.admin.search_fields_for_user, expected)

    def test_ordering_for_user(self):
        """Тест ordering для користувача"""
        expected = ('user__email',)
        self.assertEqual(self.admin.ordering_for_user, expected)

    def test_list_per_page(self):
        """Тест кількості елементів на сторінці"""
        self.assertEqual(self.admin.list_per_page, 25)


class AdminActionTest(TestCase):
    """Тести для admin actions"""

    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(CustomUser, self.site)

    def test_make_active_action_exists(self):
        """Тест наявності дії make_active"""
        from users.admin import make_active
        self.assertIn(make_active, self.admin.actions)

    def test_make_active_action_description(self):
        """Тест опису дії make_active"""
        from users.admin import make_active
        self.assertTrue(hasattr(make_active, 'short_description'))
