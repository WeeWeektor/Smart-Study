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

    def _test_activate_language(self, admin_instance, language='uk'):
        request = DummyRequest(cookies={'django_language': language})
        initial_lang = get_language()
        admin_instance.get_form(request)
        self.assertEqual(get_language(), language)
        activate(initial_lang)

    def test_get_form_activates_language_custom_user(self):
        self._test_activate_language(self.admin_custom_user)

    def test_get_form_activates_language_user_profile(self):
        self._test_activate_language(self.admin_user_profile)

    def test_get_form_activates_language_user_settings(self):
        self._test_activate_language(self.admin_user_settings)


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
            ('user', 'location', 'organization', 'specialization', 'education_level')
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ('education_level', 'organization'))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ('user__email', 'user__name', 'user__surname', 'organization', 'specialization')
        )

    def test_fieldsets_defined(self):
        self.assertTrue(hasattr(self.admin, 'fieldsets'))
        self.assertTrue(len(self.admin.fieldsets) > 0)


class UserSettingsAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserSettingsAdmin(UserSettings, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ('user', 'email_notifications', 'push_notifications', 'show_profile_to_others')
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ('email_notifications', 'push_notifications', 'deadline_reminders'))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ('user__email', 'user__name', 'user__surname'))

    def test_fieldsets_defined(self):
        self.assertTrue(hasattr(self.admin, 'fieldsets'))
        self.assertTrue(len(self.admin.fieldsets) > 0)
